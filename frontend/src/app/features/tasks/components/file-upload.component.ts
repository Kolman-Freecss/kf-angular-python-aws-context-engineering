import { CommonModule } from '@angular/common';
import { Component, EventEmitter, inject, Input, Output, signal } from '@angular/core';
import { FileService, TaskFile } from '../../../core/services/file.service';

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="file-upload-container">
      <div class="file-upload-area" 
           (dragover)="onDragOver($event)"
           (dragleave)="onDragLeave($event)"
           (drop)="onDrop($event)"
           [class.drag-over]="isDragOver()"
           [class.uploading]="uploading()">
        
        <input 
          type="file" 
          #fileInput
          (change)="onFileSelected($event)"
          multiple
          accept=".jpg,.jpeg,.png,.gif,.webp,.pdf,.txt,.doc,.docx,.rtf,.xls,.xlsx,.csv,.ppt,.pptx,.zip,.rar,.7z,.tar,.gz"
          data-testid="file-input"
          style="display: none;">
        
        <div *ngIf="!uploading()" class="upload-content">
          <div class="upload-icon">📁</div>
          <h4>Drop files here or click to browse</h4>
          <p>Supported formats: Images, PDFs, Documents, Spreadsheets, Presentations, Archives</p>
          <p class="file-limit">Maximum file size: 10MB</p>
          <button 
            class="btn-primary"
            (click)="fileInput.click()"
            data-testid="browse-files-btn">
            Browse Files
          </button>
        </div>

        <div *ngIf="uploading()" class="upload-progress">
          <div class="progress-icon">⏳</div>
          <h4>Uploading files...</h4>
          <div class="progress-bar">
            <div class="progress-fill" [style.width.%]="uploadProgress()"></div>
          </div>
          <p>{{ uploadProgress() }}% complete</p>
        </div>
      </div>

      <!-- File List -->
      <div *ngIf="files().length > 0" class="file-list">
        <h4>Attached Files ({{ files().length }})</h4>
        <div class="file-items">
          <div *ngFor="let file of files(); trackBy: trackByFileId" class="file-item">
            <div class="file-info">
              <span class="file-icon">{{ getFileIcon(file.content_type) }}</span>
              <div class="file-details">
                <div class="file-name">{{ file.original_filename }}</div>
                <div class="file-meta">
                  {{ formatFileSize(file.file_size) }} • {{ formatDate(file.created_at) }}
                </div>
              </div>
            </div>
            <div class="file-actions">
              <button 
                class="btn-icon"
                (click)="downloadFile(file)"
                data-testid="download-file-btn"
                [attr.aria-label]="'Download ' + file.original_filename">
                ⬇️
              </button>
              <button 
                class="btn-icon btn-danger"
                (click)="deleteFile(file)"
                data-testid="delete-file-btn"
                [attr.aria-label]="'Delete ' + file.original_filename">
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Error Messages -->
      <div *ngIf="error()" class="error-message">
        {{ error() }}
      </div>
    </div>
  `,
  styles: [`
    .file-upload-container {
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      overflow: hidden;
    }

    .file-upload-area {
      border: 2px dashed #bdc3c7;
      border-radius: 8px;
      padding: 2rem;
      text-align: center;
      transition: all 0.3s ease;
      cursor: pointer;
      margin: 1rem;
    }

    .file-upload-area:hover {
      border-color: #3498db;
      background-color: #f8f9fa;
    }

    .file-upload-area.drag-over {
      border-color: #3498db;
      background-color: #e3f2fd;
      transform: scale(1.02);
    }

    .file-upload-area.uploading {
      border-color: #f39c12;
      background-color: #fef5e7;
      cursor: not-allowed;
    }

    .upload-content, .upload-progress {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
    }

    .upload-icon, .progress-icon {
      font-size: 3rem;
      opacity: 0.7;
    }

    .upload-content h4, .upload-progress h4 {
      margin: 0;
      color: #2c3e50;
      font-size: 1.2rem;
    }

    .upload-content p {
      margin: 0;
      color: #7f8c8d;
      font-size: 0.9rem;
    }

    .file-limit {
      font-size: 0.8rem !important;
      color: #95a5a6 !important;
    }

    .btn-primary {
      background-color: #3498db;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 500;
      transition: background-color 0.3s;
    }

    .btn-primary:hover {
      background-color: #2980b9;
    }

    .progress-bar {
      width: 100%;
      max-width: 300px;
      height: 8px;
      background-color: #ecf0f1;
      border-radius: 4px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background-color: #3498db;
      transition: width 0.3s ease;
    }

    .file-list {
      padding: 1rem;
      border-top: 1px solid #ecf0f1;
    }

    .file-list h4 {
      margin: 0 0 1rem 0;
      color: #2c3e50;
      font-size: 1rem;
    }

    .file-items {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .file-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem;
      background-color: #f8f9fa;
      border-radius: 6px;
      transition: background-color 0.2s;
    }

    .file-item:hover {
      background-color: #e9ecef;
    }

    .file-info {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex: 1;
    }

    .file-icon {
      font-size: 1.5rem;
    }

    .file-details {
      flex: 1;
    }

    .file-name {
      font-weight: 500;
      color: #2c3e50;
      margin-bottom: 0.25rem;
    }

    .file-meta {
      font-size: 0.8rem;
      color: #7f8c8d;
    }

    .file-actions {
      display: flex;
      gap: 0.5rem;
    }

    .btn-icon {
      background: none;
      border: none;
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 4px;
      font-size: 1rem;
      transition: background-color 0.2s;
    }

    .btn-icon:hover {
      background-color: #ecf0f1;
    }

    .btn-danger:hover {
      background-color: #e74c3c;
      color: white;
    }

    .error-message {
      background-color: #fdf2f2;
      border: 1px solid #fecaca;
      color: #e74c3c;
      padding: 0.75rem;
      margin: 1rem;
      border-radius: 4px;
      font-size: 0.9rem;
    }

    @media (max-width: 768px) {
      .file-upload-area {
        padding: 1.5rem;
      }

      .upload-icon, .progress-icon {
        font-size: 2rem;
      }

      .file-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
      }

      .file-actions {
        align-self: flex-end;
      }
    }
  `]
})
export class FileUploadComponent {
  @Input() taskId!: number;
  @Output() filesUpdated = new EventEmitter<TaskFile[]>();

  private fileService = inject(FileService);

  // Signals for reactive state management
  files = signal<TaskFile[]>([]);
  uploading = signal(false);
  uploadProgress = signal(0);
  isDragOver = signal(false);
  error = signal<string | null>(null);

  ngOnInit(): void {
    this.loadFiles();
  }

  loadFiles(): void {
    this.fileService.getTaskFiles(this.taskId).subscribe({
      next: (files) => {
        this.files.set(files);
        this.filesUpdated.emit(files);
      },
      error: (err) => {
        this.error.set('Failed to load files');
        console.error('Error loading files:', err);
      }
    });
  }

  onFileSelected(event: Event): void {
    const target = event.target as HTMLInputElement;
    const selectedFiles = target.files;
    if (selectedFiles && selectedFiles.length > 0) {
      this.uploadFiles(Array.from(selectedFiles));
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver.set(true);
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver.set(false);
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver.set(false);
    
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.uploadFiles(Array.from(files));
    }
  }

  uploadFiles(files: File[]): void {
    if (files.length === 0) return;

    this.uploading.set(true);
    this.error.set(null);
    this.uploadProgress.set(0);

    let completedUploads = 0;
    const totalFiles = files.length;

    files.forEach(file => {
      this.fileService.uploadFileWithProgress(this.taskId, file).subscribe({
        next: (response) => {
          if ('percentage' in response) {
            // Progress update
            const currentProgress = (completedUploads + response.percentage) / totalFiles;
            this.uploadProgress.set(Math.round(currentProgress));
          } else {
            // Upload completed
            completedUploads++;
            if (completedUploads === totalFiles) {
              this.uploading.set(false);
              this.uploadProgress.set(100);
              this.loadFiles(); // Reload files list
              setTimeout(() => this.uploadProgress.set(0), 1000);
            }
          }
        },
        error: (err) => {
          this.uploading.set(false);
          this.error.set(`Failed to upload ${file.name}: ${err.message || 'Unknown error'}`);
          console.error('Error uploading file:', err);
        }
      });
    });
  }

  downloadFile(file: TaskFile): void {
    this.fileService.downloadFile(file.id).subscribe({
      next: (response) => {
        // Create a temporary link to download the file
        const link = document.createElement('a');
        link.href = response.download_url;
        link.download = response.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      },
      error: (err) => {
        this.error.set('Failed to download file');
        console.error('Error downloading file:', err);
      }
    });
  }

  deleteFile(file: TaskFile): void {
    if (confirm(`Are you sure you want to delete "${file.original_filename}"?`)) {
      this.fileService.deleteFile(file.id).subscribe({
        next: () => {
          this.loadFiles(); // Reload files list
        },
        error: (err) => {
          this.error.set('Failed to delete file');
          console.error('Error deleting file:', err);
        }
      });
    }
  }

  formatFileSize(bytes: number): string {
    return this.fileService.formatFileSize(bytes);
  }

  getFileIcon(contentType: string): string {
    return this.fileService.getFileIcon(contentType);
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString();
  }

  trackByFileId(index: number, file: TaskFile): number {
    return file.id;
  }
}
