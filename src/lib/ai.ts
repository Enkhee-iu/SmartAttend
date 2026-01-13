// AI Service for Face Recognition using Luxand Cloud API
// Documentation: https://luxand.cloud/

export interface FaceRecognitionResult {
  success: boolean;
  userId?: string;
  confidence?: number;
  faceId?: string; // Luxand person UUID
  error?: string;
}

export interface FaceEmbedding {
  embedding: number[];
  faceId: string;
}

interface LuxandPersonResponse {
  status: 'success' | 'error';
  uuid?: string;
  message?: string;
}

interface LuxandRecognitionResponse {
  status?: 'success' | 'error';
  [key: string]: unknown;
}

/**
 * Convert image data to Blob/Buffer for FormData
 * In Node.js/server-side, FormData accepts Buffer directly
 */
function imageToFormDataValue(imageData: string | Buffer): string | Buffer | Blob {
  if (typeof imageData === 'string') {
    // Check if it's a URL
    if (imageData.indexOf('https://') === 0) {
      return imageData;
    }
    // Base64 data URL - convert to Buffer
    const base64Data = imageData.replace(/^data:image\/\w+;base64,/, '');
    return Buffer.from(base64Data, 'base64');
  }
  // Buffer - use directly (FormData accepts Buffer in Node.js)
  return imageData;
}

/**
 * Recognize face from image data using Luxand Cloud API
 * @param imageData - Base64 encoded image, Buffer, or image URL
 * @returns Face recognition result
 */
export async function recognizeFace(imageData: string | Buffer): Promise<FaceRecognitionResult> {
  try {
    const apiToken = process.env.LUXAND_API_TOKEN || process.env.AI_API_KEY;

    if (!apiToken) {
      console.warn('LUXAND_API_TOKEN not configured, using mock recognition');
      return mockFaceRecognition(imageData);
    }

    // Prepare FormData
    const formData = new FormData();
    const photo = imageToFormDataValue(imageData);
    
    if (typeof photo === 'string') {
      formData.append('photo', photo);
    } else {
      // Buffer or Blob - FormData accepts Buffer directly in Node.js
      formData.append('photo', photo as Blob, 'photo.jpg');
    }

    // Call Luxand API for face recognition
    const response = await fetch('https://api.luxand.cloud/photo/search/v2', {
      method: 'POST',
      headers: {
        'token': apiToken,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Luxand API error: ${response.status} ${errorText}`);
    }

    const data = (await response.json()) as LuxandRecognitionResponse[];

    // Luxand returns an array of recognized people
    if (Array.isArray(data) && data.length > 0) {
      const firstMatch = data[0];
      // Extract UUID and confidence from Luxand response
      const personUuid = (firstMatch as { uuid?: string }).uuid;
      const confidence = (firstMatch as { similarity?: number }).similarity || 0;

      if (personUuid) {
        return {
          success: true,
          faceId: personUuid,
          confidence: confidence,
        };
      }
    }

    return {
      success: false,
      error: 'Face not recognized',
    };
  } catch (error) {
    console.error('Face recognition error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Face recognition failed',
    };
  }
}

/**
 * Register/Enroll a person with Luxand Cloud API
 * @param userId - User ID (will be used as person name)
 * @param imageData - Base64 encoded image, Buffer, or image URL
 * @param personName - Optional person name (defaults to userId)
 * @returns Registration result with faceId (person UUID)
 */
export async function registerFace(
  userId: string,
  imageData: string | Buffer,
  personName?: string
): Promise<{ success: boolean; faceId?: string; error?: string }> {
  try {
    const apiToken = process.env.LUXAND_API_TOKEN || process.env.AI_API_KEY;

    if (!apiToken) {
      console.warn('LUXAND_API_TOKEN not configured, using mock registration');
      return { success: true, faceId: `mock-face-id-${userId}-${Date.now()}` };
    }

    // Prepare FormData
    const formData = new FormData();
    formData.append('name', personName || userId);
    
    const photo = imageToFormDataValue(imageData);
    if (typeof photo === 'string') {
      formData.append('photos', photo);
    } else {
      // Buffer or Blob - FormData accepts Buffer directly in Node.js
      formData.append('photos', photo as Blob, 'photo.jpg');
    }
    
    formData.append('store', '1');
    // Optional: Add to a collection (can be configured via env)
    const collection = process.env.LUXAND_COLLECTION;
    if (collection) {
      formData.append('collections', collection);
    }

    // Call Luxand API to create person
    const response = await fetch('https://api.luxand.cloud/v2/person', {
      method: 'POST',
      headers: {
        'token': apiToken,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Luxand API error: ${response.status} ${errorText}`);
    }

    const data = (await response.json()) as LuxandPersonResponse;

    if (data.status === 'success' && data.uuid) {
      return {
        success: true,
        faceId: data.uuid,
      };
    }

    throw new Error(data.message || 'Person registration failed');
  } catch (error) {
    console.error('Face registration error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Face registration failed',
    };
  }
}

/**
 * Add additional face to an existing person (improves recognition accuracy)
 * @param personUuid - Luxand person UUID
 * @param imageData - Base64 encoded image, Buffer, or image URL
 * @returns Success status
 */
export async function addFaceToPerson(
  personUuid: string,
  imageData: string | Buffer
): Promise<{ success: boolean; error?: string }> {
  try {
    const apiToken = process.env.LUXAND_API_TOKEN || process.env.AI_API_KEY;

    if (!apiToken) {
      console.warn('LUXAND_API_TOKEN not configured');
      return { success: false, error: 'API token not configured' };
    }

    // Prepare FormData
    const formData = new FormData();
    
    const photo = imageToFormDataValue(imageData);
    if (typeof photo === 'string') {
      formData.append('photos', photo);
    } else {
      // Buffer or Blob - FormData accepts Buffer directly in Node.js
      formData.append('photos', photo as Blob, 'photo.jpg');
    }
    
    formData.append('store', '1');

    // Call Luxand API to add face to person
    const response = await fetch(`https://api.luxand.cloud/v2/person/${personUuid}`, {
      method: 'POST',
      headers: {
        'token': apiToken,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Luxand API error: ${response.status} ${errorText}`);
    }

    const data = (await response.json()) as LuxandPersonResponse;

    if (data.status === 'success') {
      return { success: true };
    }

    throw new Error(data.message || 'Failed to add face to person');
  } catch (error) {
    console.error('Add face error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to add face',
    };
  }
}

/**
 * Extract face embedding from image
 * @param imageData - Base64 encoded image or image buffer
 * @returns Face embedding vector (not directly supported by Luxand, returns null)
 */
export async function extractFaceEmbedding(imageData: string | Buffer): Promise<number[] | null> {
  // Luxand Cloud API doesn't expose face embeddings directly
  // This would require a different service or Luxand's enterprise features
  console.warn('Face embedding extraction not available with Luxand Cloud API');
  return null;
}

/**
 * Mock face recognition for development/testing
 */
function mockFaceRecognition(imageData: string | Buffer): FaceRecognitionResult {
  // Mock implementation for development
  // In production, this should never be called if API key is configured
  return {
    success: true,
    userId: 'mock-user-id',
    confidence: 0.95,
    faceId: `mock-face-${Date.now()}`,
  };
}

/**
 * Compare two face embeddings using cosine similarity
 * @param embedding1 - First face embedding
 * @param embedding2 - Second face embedding
 * @returns Similarity score (0-1, where 1 is identical)
 */
export function compareFaceEmbeddings(embedding1: number[], embedding2: number[]): number {
  if (embedding1.length !== embedding2.length) {
    throw new Error('Embeddings must have the same length');
  }

  // Cosine similarity
  let dotProduct = 0;
  let norm1 = 0;
  let norm2 = 0;

  for (let i = 0; i < embedding1.length; i++) {
    dotProduct += embedding1[i] * embedding2[i];
    norm1 += embedding1[i] * embedding1[i];
    norm2 += embedding2[i] * embedding2[i];
  }

  const similarity = dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
  return Math.max(0, Math.min(1, similarity)); // Clamp between 0 and 1
}
