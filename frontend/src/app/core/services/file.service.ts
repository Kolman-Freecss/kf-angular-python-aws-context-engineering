import { HttpClient, HttpEvent, HttpEventType, HttpProgressEvent } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface TaskFile {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  content_type: string;
  task_id: number;
  user_id: number;
  s3_key: string;
  s3_bucket: string;
  created_at: string;
}

export interface FileUploadResponse {
  file_id: number;
  filename: string;
  file_size: number;
  content_type: string;
  upload_url?: string;
  message: string;
}

export interface FileDownloadResponse {
  download_url: string;
  filename: string;
  content_type: string;
  file_size: number;
}

export interface FileUploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

@Injectable({
  providedIn: 'root'
})
export class FileService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api`;

  // File validation
  private readonly maxFileSize = 10 * 1024 * 1024; // 10MB
  private readonly allowedTypes = [
    // Images
    'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
    // Documents
    'application/pdf', 'text/plain', 'application/msword', 
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/rtf',
    // Spreadsheets
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv',
    // Presentations
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    // Archives
    'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed',
    'application/x-tar', 'application/gzip'
  ];

  private readonly allowedExtensions = [
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'txt', 'doc', 'docx', 'rtf',
    'xls', 'xlsx', 'csv', 'ppt', 'pptx', 'zip', 'rar', '7z', 'tar', 'gz'
  ];

  validateFile(file: File): { valid: boolean; error?: string } {
    // Check file size
    if (file.size > this.maxFileSize) {
      return {
        valid: false,
        error: `File size exceeds maximum allowed size of ${this.maxFileSize / (1024 * 1024)}MB`
      };
    }

    // Check file type
    if (!this.allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: 'File type is not allowed. Please upload images, documents, spreadsheets, presentations, or archives.'
      };
    }

    // Check file extension
    const extension = file.name.split('.').pop()?.toLowerCase();
    if (!extension || !this.allowedExtensions.includes(extension)) {
      return {
        valid: false,
        error: 'File extension is not allowed. Please check the file type.'
      };
    }

    return { valid: true };
  }

  uploadFile(taskId: number, file: File): Observable<FileUploadResponse> {
    const validation = this.validateFile(file);
    if (!validation.valid) {
      throw new Error(validation.error);
    }

    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<FileUploadResponse>(
      `${this.apiUrl}/tasks/${taskId}/files`,
      formData
    );
  }

  uploadFileWithProgress(taskId: number, file: File): Observable<FileUploadProgress | FileUploadResponse> {
    const validation = this.validateFile(file);
    if (!validation.valid) {
      throw new Error(validation.error);
    }

    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<FileUploadResponse>(
      `${this.apiUrl}/tasks/${taskId}/files`,
      formData,
      {
        reportProgress: true,
        observe: 'events'
      }
    ).pipe(
      map((event: HttpEvent<FileUploadResponse>) => {
        switch (event.type) {
          case HttpEventType.UploadProgress:
            const progressEvent = event as HttpProgressEvent;
            return {
              loaded: progressEvent.loaded,
              total: progressEvent.total || 0,
              percentage: Math.round(100 * progressEvent.loaded / (progressEvent.total || 1))
            } as FileUploadProgress;
          case HttpEventType.Response:
            return event.body!;
          default:
            return {} as FileUploadProgress;
        }
      })
    );
  }

  getTaskFiles(taskId: number): Observable<TaskFile[]> {
    return this.http.get<{ files: TaskFile[]; total: number }>(
      `${this.apiUrl}/tasks/${taskId}/files`
    ).pipe(
      map(response => response.files)
    );
  }

  downloadFile(fileId: number): Observable<FileDownloadResponse> {
    return this.http.get<FileDownloadResponse>(`${this.apiUrl}/files/${fileId}/download`);
  }

  deleteFile(fileId: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/files/${fileId}`);
  }

  getFileInfo(fileId: number): Observable<TaskFile> {
    return this.http.get<TaskFile>(`${this.apiUrl}/files/${fileId}`);
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  getFileIcon(contentType: string): string {
    if (contentType.startsWith('image/')) return '🖼️';
    if (contentType.includes('pdf')) return '📄';
    if (contentType.includes('word') || contentType.includes('document')) return '📝';
    if (contentType.includes('excel') || contentType.includes('spreadsheet')) return '📊';
    if (contentType.includes('powerpoint') || contentType.includes('presentation')) return '📽️';
    if (contentType.includes('zip') || contentType.includes('rar') || contentType.includes('archive')) return '📦';
    if (contentType.includes('text')) return '📄';
    return '📎';
  }
}
