"""
API endpoints for AI model inference.

This module contains endpoints for running anomaly detection inference
using ONNX models.
"""

import time
import base64
import numpy as np
from io import BytesIO
from PIL import Image
from typing import Optional
from fastapi import APIRouter, HTTPException, status
import onnxruntime as ort
import os

from ..core.config import settings
from ..schemas import InferenceRequest, InferenceResponse

router = APIRouter()

# Global variables to cache loaded models
_standard_model = None
_quantized_model = None


def load_onnx_model(model_path: str) -> ort.InferenceSession:
    """
    Load an ONNX model.

    Args:
        model_path: Path to the ONNX model file.

    Returns:
        ONNX InferenceSession.

    Raises:
        FileNotFoundError: If model file doesn't exist.
        Exception: If model loading fails.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    try:
        session = ort.InferenceSession(model_path)
        return session
    except Exception as e:
        raise Exception(f"Failed to load ONNX model: {str(e)}")


def get_model(model_type: str) -> ort.InferenceSession:
    """
    Get cached model or load it if not cached.

    Args:
        model_type: Type of model ('standard' or 'quantized').

    Returns:
        ONNX InferenceSession.
    """
    global _standard_model, _quantized_model

    if model_type == "standard":
        if _standard_model is None:
            model_path = os.path.join(os.getcwd(), settings.ONNX_MODEL_PATH)
            _standard_model = load_onnx_model(model_path)
        return _standard_model
    elif model_type == "quantized":
        if _quantized_model is None:
            model_path = os.path.join(os.getcwd(), settings.QUANTIZED_MODEL_PATH)
            _quantized_model = load_onnx_model(model_path)
        return _quantized_model
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def preprocess_image(image_data: bytes, target_size: tuple = (224, 224)) -> np.ndarray:
    """
    Preprocess image for model inference.

    Args:
        image_data: Raw image bytes.
        target_size: Target image size (width, height).

    Returns:
        Preprocessed image as numpy array.
    """
    try:
        # Open image from bytes
        image = Image.open(BytesIO(image_data))

        # Convert to RGB if necessary
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize image
        image = image.resize(target_size, Image.Resampling.LANCZOS)

        # Convert to numpy array and normalize
        image_array = np.array(image, dtype=np.float32)

        # Normalize to [0, 1] range
        image_array = image_array / 255.0

        # Add batch dimension and rearrange to NCHW format (batch, channel, height, width)
        image_array = np.transpose(image_array, (2, 0, 1))  # HWC to CHW
        image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension

        return image_array

    except Exception as e:
        raise Exception(f"Error preprocessing image: {str(e)}")


def postprocess_prediction(output: np.ndarray, threshold: float = 0.5) -> tuple:
    """
    Postprocess model output to get final prediction.

    Args:
        output: Raw model output.
        threshold: Threshold for anomaly classification.

    Returns:
        Tuple of (prediction_score, is_anomaly, confidence).
    """
    try:
        # Assuming binary classification with sigmoid output
        if output.shape[-1] == 1:
            # Single output (anomaly score)
            prediction_score = float(output[0][0])
        else:
            # Multiple outputs, take the probability of positive class
            prediction_score = (
                float(output[0][1])
                if output.shape[-1] == 2
                else float(np.max(output[0]))
            )

        # Apply sigmoid if needed (in case output is logit)
        if prediction_score > 1.0 or prediction_score < 0.0:
            prediction_score = 1.0 / (1.0 + np.exp(-prediction_score))

        # Determine if it's an anomaly
        is_anomaly = prediction_score > threshold

        # Calculate confidence (distance from threshold)
        confidence = abs(prediction_score - threshold) / threshold
        confidence = min(confidence, 1.0)  # Cap at 1.0

        return prediction_score, is_anomaly, confidence

    except Exception as e:
        raise Exception(f"Error postprocessing prediction: {str(e)}")


@router.post("/predict", response_model=InferenceResponse)
async def predict_anomaly(request: InferenceRequest):
    """
    Run anomaly detection inference on an image.

    Args:
        request: Inference request containing image and model type.

    Returns:
        InferenceResponse with prediction results.
    """
    start_time = time.time()

    try:
        # Decode base64 image
        try:
            image_data = base64.b64decode(request.image)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid base64 image data: {str(e)}",
            )

        # Load model
        try:
            model = get_model(request.model_type)
        except FileNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error loading model: {str(e)}",
            )

        # Preprocess image
        try:
            processed_image = preprocess_image(image_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing image: {str(e)}",
            )

        # Run inference
        try:
            input_name = model.get_inputs()[0].name
            output = model.run(None, {input_name: processed_image})
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error running inference: {str(e)}",
            )

        # Postprocess results
        try:
            prediction_score, is_anomaly, confidence = postprocess_prediction(output[0])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error postprocessing results: {str(e)}",
            )

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        return InferenceResponse(
            prediction=prediction_score,
            is_anomaly=is_anomaly,
            confidence=confidence,
            model_used=request.model_type,
            processing_time_ms=processing_time_ms,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during inference: {str(e)}",
        )


@router.get("/models/status")
async def get_models_status():
    """
    Check the status of available models.

    Returns:
        Status information for available models.
    """
    try:
        status_info = {
            "standard_model": {
                "path": settings.ONNX_MODEL_PATH,
                "exists": os.path.exists(
                    os.path.join(os.getcwd(), settings.ONNX_MODEL_PATH)
                ),
                "loaded": _standard_model is not None,
            },
            "quantized_model": {
                "path": settings.QUANTIZED_MODEL_PATH,
                "exists": os.path.exists(
                    os.path.join(os.getcwd(), settings.QUANTIZED_MODEL_PATH)
                ),
                "loaded": _quantized_model is not None,
            },
        }

        return status_info

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking model status: {str(e)}",
        )


@router.post("/models/preload")
async def preload_models():
    """
    Preload all available models into memory.

    Returns:
        Status of preloaded models.
    """
    try:
        results = {}

        # Try to preload standard model
        try:
            get_model("standard")
            results["standard_model"] = "loaded"
        except Exception as e:
            results["standard_model"] = f"failed: {str(e)}"

        # Try to preload quantized model
        try:
            get_model("quantized")
            results["quantized_model"] = "loaded"
        except Exception as e:
            results["quantized_model"] = f"failed: {str(e)}"

        return {"message": "Model preloading completed", "results": results}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error preloading models: {str(e)}",
        )
