import { useState } from 'react';
import { SelectProps } from '@cloudscape-design/components';
import { OcsfCategoryEnum, OcsfVersionEnum, TransformLanguageEnum } from '../generated-api-client';
import { createTransformerLogic } from '../utils/transformerClient';
import { ExtractionPattern, Transformer } from '../utils/types';

export interface TransformerState {
  isLoading: boolean;
  error: string | null;
  transformer: Transformer | null;
  createTransformer: () => Promise<void>;
  clearTransformer: () => void;
}

interface TransformerStateProps {
  logs: string[];
  selectedLogIds: string[];
  categoryValue?: string;
  versionValue?: OcsfVersionEnum;
  extractionPatterns: ExtractionPattern[];
  language: SelectProps.Option;
}

const useTransformerState = ({
  logs,
  selectedLogIds,
  categoryValue,
  versionValue,
  extractionPatterns,
  language,
}: TransformerStateProps): TransformerState => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [transformer, setTransformer] = useState<Transformer | null>(null);
  
  const handleCreateTransformer = async () => {
    // Validate inputs
    if (!selectedLogIds.length || !categoryValue) {
      setError("Please select a log entry and category before creating a transformer");
      return;
    }

    if (extractionPatterns.length === 0) {
      setError("Please extract entities first to create patterns for transformation");
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      // Get the selected log entry
      const selectedLogEntry = logs[parseInt(selectedLogIds[0])];
      
      // Get transform language value
      const transformLanguage = language.value as TransformLanguageEnum;

      // Call the transformer client function
      const response = await createTransformerLogic(
        transformLanguage,
        categoryValue,
        selectedLogEntry,
        extractionPatterns,
        versionValue
      );
      
      // Update state with the response
      setTransformer(response.transformer);
    } catch (error) {
      console.error('Error creating transformer:', error);
      setError('Failed to create transformer. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const clearTransformer = () => {
    setTransformer(null);
    setError(null);
  };

  return {
    isLoading,
    error,
    transformer,
    createTransformer: handleCreateTransformer,
    clearTransformer,
  };
};

export default useTransformerState;
