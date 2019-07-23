package com.masterthesis.johannes.annotationtool

import android.graphics.Canvas.EdgeType
import android.graphics.RectF
import android.R.attr.y
import android.R.attr.x
import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.view.View


class MyMarkersView(context: Context) : View(context) {

    private var scale = 1f
    private val markers = HashSet<MyMarker>()
    private var locationPin:Bitmap

    init {
        val density = resources.displayMetrics.densityDpi.toFloat()
        locationPin = getBitmapFromVectorDrawable(context,R.drawable.my_location)
        var w = density / 200f * locationPin.width
        var h = density / 200f * locationPin.height
        locationPin = Bitmap.createScaledBitmap(locationPin, w.toInt(), h.toInt(), true)

    }

    override protected fun onDraw(canvas: Canvas) {
        for (marker in markers) {

            // use the translator to translate and scale to the correct position on the TileView's coordinate system
            val adaptedX = marker.x
            val adaptedY = marker.y
            val left = adaptedX - MARKER_SIZE * scale
            val top = adaptedY - MARKER_SIZE * scale
            val right = adaptedX + MARKER_SIZE * scale
            val bottom = adaptedY + MARKER_SIZE * scale
            val markerBounds = RectF(left, top, right, bottom)

            // don't draw if outside the current display viewport
            if (!canvas.quickReject(markerBounds, Canvas.EdgeType.BW) && scale>3) {
                // draw the marker bitmap
                canvas.drawBitmap(marker.bitmap, null, markerBounds, null)
            }
        }
    }

    fun onScale(scale: Float) {
        this.scale = scale
        invalidate()
    }

    fun addMarker(marker: MyMarker) {
        markers.add(marker)
        invalidate()
    }


    companion object {

        private val MARKER_SIZE = 20
    }

}
