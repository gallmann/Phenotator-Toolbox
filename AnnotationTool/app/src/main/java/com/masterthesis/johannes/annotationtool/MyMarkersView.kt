package com.masterthesis.johannes.annotationtool

import android.graphics.Canvas.EdgeType
import android.graphics.RectF
import android.R.attr.y
import android.R.attr.x
import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.view.View
import com.moagrius.tileview.TileView


class MyMarkersView(context: Context, tileView:MyTileView) : View(context) {




    private var scale = 1f
    private val markers = HashSet<MyMarker>()
    private var locationPin:Bitmap
    private val MARKER_SIZE = 20
    init {
        tileView.addListener(this)
        val density = resources.displayMetrics.densityDpi.toFloat()
        locationPin = getBitmapFromVectorDrawable(context,R.drawable.my_location)
        var w = density / 200f * locationPin.width
        var h = density / 200f * locationPin.height
        locationPin = Bitmap.createScaledBitmap(locationPin, w.toInt(), h.toInt(), true)

    }

    override protected fun onDraw(canvas: Canvas) {

        println(scale)
        for (marker in markers) {

            // use the translator to translate and scale to the correct position on the TileView's coordinate system
            val adaptedX = marker.x * scale
            val adaptedY = marker.y * scale
            val left = adaptedX - MARKER_SIZE
            val top = adaptedY - MARKER_SIZE
            val right = adaptedX + MARKER_SIZE
            val bottom = adaptedY + MARKER_SIZE
            val markerBounds = RectF(left, top, right, bottom)

            // don't draw if outside the current display viewport
            if (!canvas.quickReject(markerBounds, Canvas.EdgeType.BW)) {
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


}
