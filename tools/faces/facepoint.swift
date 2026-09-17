// Face focal points via Apple's Vision framework (no third-party dependency, nothing leaves the Mac).
//   swiftc -O tools/faces/facepoint.swift -o /tmp/facepoint && /tmp/facepoint <image> [<image>...]
// Prints one JSON line per image: {"path":..., "faces":n, "x":0..1, "y":0..1, "fw":..., "fh":...}
// fw/fh are the largest face's width and height as a fraction of the image, so a portrait can be
// recropped to put every head at the same size.
// x,y is the area-weighted centre of every face found, in image coordinates with y measured from the
// top, which is what CSS object-position wants. No faces: nothing is printed for that file.
import Foundation
import Vision
import CoreImage

for path in CommandLine.arguments.dropFirst() {
    guard let img = CIImage(contentsOf: URL(fileURLWithPath: path)) else { continue }
    let req = VNDetectFaceRectanglesRequest()
    let handler = VNImageRequestHandler(ciImage: img, options: [:])
    do { try handler.perform([req]) } catch { continue }
    guard let faces = req.results, !faces.isEmpty else { continue }
    var sx = 0.0, sy = 0.0, sw = 0.0
    var big = 0.0, fw = 0.0, fh = 0.0, bx = 0.0, by = 0.0
    for f in faces {
        let b = f.boundingBox                    // normalised, origin bottom-left
        let w = b.width * b.height               // weight big faces more
        sx += (b.midX) * w
        sy += (1 - b.midY) * w                   // flip to top-left origin
        sw += w
        if w > big { big = w; fw = b.width; fh = b.height; bx = b.midX; by = 1 - b.midY }
    }
    let x = sx / sw, y = sy / sw
    print("{\"path\":\"\(path)\",\"faces\":\(faces.count),\"x\":\(String(format: "%.4f", x)),\"y\":\(String(format: "%.4f", y)),\"fw\":\(String(format: "%.4f", fw)),\"fh\":\(String(format: "%.4f", fh)),\"bx\":\(String(format: "%.4f", bx)),\"by\":\(String(format: "%.4f", by))}")
}
