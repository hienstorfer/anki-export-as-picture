(define (crop-whitespace image drawable)
  (gimp-image-lower-item-to-bottom image drawable)
  (gimp-selection-all image)
  (gimp-selection-shrink image 1)
  (gimp-selection-grow image 1)
  (gimp-selection-none image)
  (gimp-image-crop-to-content image))

(define (batch-crop-whitespace pattern)
  (let* ((filelist (cadr (file-glob pattern 1))))
    (while (not (null? filelist))
      (let* ((filename (car filelist))
             (image (car (gimp-file-load RUN-NONINTERACTIVE filename filename)))
             (drawable (car (gimp-image-get-active-layer image))))
        (crop-whitespace image drawable)
        (gimp-file-save RUN-NONINTERACTIVE image drawable filename filename)
        (gimp-image-delete image))
      (set! filelist (cdr filelist)))))

(script-fu-register
  "batch-crop-whitespace"
  "Batch Crop Whitespace"
  "Crops whitespace from all images matching a pattern"
  "Your Name"
  "Your Name"
  "2024"
  ""
  SF-STRING "File pattern" "*.jpg")

(script-fu-menu-register "batch-crop-whitespace" "<Image>/Filters/Batch")
