// Apple Vision for effetti-video: your face and your person matte, one frame at a time.
//
//     vision_stream <width> <height>
//
// Compiled and run by apple_vision.py, never by hand. Reads frames from stdin, each
// width*height*4 bytes of BGRA, and answers each one on stdout with:
//   4 float32  face centre x, centre y, width (pixels, origin top-left), confidence (0: no face)
//   2 int32    matte width, height
//   bytes      the person matte, 8-bit, at the model's own size (the caller stretches it)
// The matte runs through one VNSequenceRequestHandler, so Vision smooths it across frames.
// EFFETTI_VISION_QUALITY=balanced trades edge quality for speed (default: accurate).
import CoreVideo
import Foundation
import Vision

let args = CommandLine.arguments
guard args.count == 3, let W = Int(args[1]), let H = Int(args[2]) else {
  FileHandle.standardError.write("usage: vision_stream <width> <height>\n".data(using: .utf8)!)
  exit(2)
}
let quality = ProcessInfo.processInfo.environment["EFFETTI_VISION_QUALITY"] ?? "accurate"
let input = FileHandle.standardInput
let output = FileHandle.standardOutput

let sequence = VNSequenceRequestHandler()
let segmentation = VNGeneratePersonSegmentationRequest()
segmentation.qualityLevel = quality == "balanced" ? .balanced : .accurate
segmentation.outputPixelFormat = kCVPixelFormatType_OneComponent8

var made: CVPixelBuffer?
CVPixelBufferCreate(kCFAllocatorDefault, W, H, kCVPixelFormatType_32BGRA,
                    [kCVPixelBufferIOSurfacePropertiesKey: [:]] as CFDictionary, &made)
guard let frame = made else { exit(3) }

func readExactly(_ n: Int) -> Data? {
  var data = Data(capacity: n)
  while data.count < n {
    let chunk = input.readData(ofLength: n - data.count)
    if chunk.isEmpty { return nil }
    data.append(chunk)
  }
  return data
}

while let bytes = readExactly(W * H * 4) {
  CVPixelBufferLockBaseAddress(frame, [])
  let base = CVPixelBufferGetBaseAddress(frame)!
  let stride = CVPixelBufferGetBytesPerRow(frame)
  bytes.withUnsafeBytes { raw in
    for y in 0..<H { memcpy(base + y * stride, raw.baseAddress! + y * W * 4, W * 4) }
  }
  CVPixelBufferUnlockBaseAddress(frame, [])

  // The largest confident face is yours.
  var face: [Float32] = [0, 0, 0, 0]
  let rects = VNDetectFaceRectanglesRequest()
  try? VNImageRequestHandler(cvPixelBuffer: frame, options: [:]).perform([rects])
  if let f = rects.results?.max(by: { $0.boundingBox.width * CGFloat($0.confidence) < $1.boundingBox.width * CGFloat($1.confidence) }) {
    let b = f.boundingBox
    face = [Float32(b.midX) * Float32(W), Float32(1 - b.midY) * Float32(H), Float32(b.width) * Float32(W), f.confidence]
  }

  var size: [Int32] = [0, 0]
  var matte = Data()
  if (try? sequence.perform([segmentation], on: frame)) != nil, let m = segmentation.results?.first?.pixelBuffer {
    CVPixelBufferLockBaseAddress(m, .readOnly)
    let w = CVPixelBufferGetWidth(m), h = CVPixelBufferGetHeight(m), row = CVPixelBufferGetBytesPerRow(m)
    let p = CVPixelBufferGetBaseAddress(m)!
    matte.reserveCapacity(w * h)
    for y in 0..<h { matte.append(Data(bytes: p + y * row, count: w)) }
    CVPixelBufferUnlockBaseAddress(m, .readOnly)
    size = [Int32(w), Int32(h)]
  }

  var reply = Data()
  face.withUnsafeBufferPointer { reply.append(Data(buffer: $0)) }
  size.withUnsafeBufferPointer { reply.append(Data(buffer: $0)) }
  reply.append(matte)
  output.write(reply)
}
