import {
  Configuration,
  TransformerApi,
  TransformerHeuristicCreateRequest,
  TransformerCategorizeV110Request,
  TransformerCategorizeRequest,
  TransformerEntitiesAnalyzeRequest,
  TransformerEntitiesExtractRequest,
  TransformerEntitiesTestRequest,
  TransformerLogicCreateRequest,
  TransformerLogicV110CreateRequest,
  OcsfCategoryEnum,
  OcsfVersionEnum,
  TransformLanguageEnum
} from '../generated-api-client';
import { API_BASE_URL } from './constants';
import { ApiError } from './types';

// Create API configuration and client
const apiConfig = new Configuration({ basePath: API_BASE_URL });
const apiClient = new TransformerApi(apiConfig);

// Centralized error handling for API calls
const handleApiError = (error: unknown): never => {
  const apiError = error as ApiError;
  
  if (apiError.response && apiError.response.data) {
    const serverErrorMessage = apiError.response.data.error || "An unknown error occurred.";
    console.error("Server error:", serverErrorMessage);
    throw new Error(`API error: ${serverErrorMessage}`);
  } else {
    console.error("Unexpected error:", apiError);
    throw new Error("An unexpected error occurred. Please try again later.");
  }
};

// Get regex heuristic recommendation
export const getRegexRecommendation = async (
  logEntry: string,
  existingPattern: string,
  guidance: string
) => {
  try {
    const payload: TransformerHeuristicCreateRequest = {
      input_entry: logEntry,
      existing_heuristic: existingPattern,
      user_guidance: guidance
    };
    const response = await apiClient.transformerHeuristicCreateCreate(payload);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

// Get OCSF category recommendation (version-flexible)
export const getCategoryRecommendation = async (
  logEntry: string,
  guidance: string,
  ocsfVersion?: OcsfVersionEnum
) => {
  try {
    const payload: TransformerCategorizeRequest = {
      input_entry: logEntry,
      user_guidance: guidance,
      ocsf_version: ocsfVersion
    };
    const response = await apiClient.transformerCategorizeCreate(payload);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

// Analyze entities in a log entry (version-flexible)
export const analyzeEntities = async (
  ocsfCategory: string,
  logEntry: string,
  ocsfVersion?: OcsfVersionEnum
) => {
  try {
    const payload: TransformerEntitiesAnalyzeRequest = {
      ocsf_category: ocsfCategory,
      input_entry: logEntry,
      ocsf_version: ocsfVersion
    };

    const response = await apiClient.transformerEntitiesAnalyzeCreate(payload);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

// Extract transformation patterns for entities (version-flexible)
export const extractEntityPatterns = async (
  transformLanguage: TransformLanguageEnum,
  ocsfCategory: string,
  logEntry: string,
  mappings: any[],
  ocsfVersion?: OcsfVersionEnum
) => {
  try {
    const payload: TransformerEntitiesExtractRequest = {
      transform_language: transformLanguage,
      ocsf_category: ocsfCategory,
      input_entry: logEntry,
      mappings: mappings,
      ocsf_version: ocsfVersion
    };

    const response = await apiClient.transformerEntitiesExtractCreate(payload);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

// Test extraction pattern (version-flexible)
export const testExtractionPattern = async (
  transformLanguage: TransformLanguageEnum,
  ocsfCategory: string,
  logEntry: string,
  pattern: any,
  ocsfVersion?: OcsfVersionEnum
) => {
  try {
    const payload: TransformerEntitiesTestRequest = {
      transform_language: transformLanguage,
      ocsf_category: ocsfCategory,
      input_entry: logEntry,
      patterns: [pattern],
      ocsf_version: ocsfVersion
    };

    const response = await apiClient.transformerEntitiesTestCreate(payload);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

// Create transformer logic (version-flexible)
export const createTransformerLogic = async (
  transformLanguage: TransformLanguageEnum,
  ocsfCategory: string,
  logEntry: string,
  patterns: any[],
  ocsfVersion?: OcsfVersionEnum
) => {
  try {
    const payload: TransformerLogicCreateRequest = {
      transform_language: transformLanguage,
      ocsf_category: ocsfCategory,
      input_entry: logEntry,
      patterns: patterns,
      ocsf_version: ocsfVersion
    };

    const response = await apiClient.transformerLogicCreateCreate(payload);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};
