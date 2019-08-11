package com.masterthesis.johannes.annotationtool

import android.graphics.Canvas.EdgeType
import android.graphics.RectF
import android.R.attr.y
import android.R.attr.x
import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Rect
import android.view.View
import com.moagrius.tileview.TileView


class MyMarkersView(context: Context, var tileView:MyTileView) : View(context), TileView.Listener {


    private var y = 0
    private var x = 0
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
        //println("--------------------------------")
        var counter = 0
        //println("x:" + x)
        //println("y:" + y)
        //println("scale:" + scale)
        var viewPort = RectF(x.toFloat()+20,y.toFloat(),(x+tileView.width-20).toFloat(),(y+tileView.height).toFloat())
        //println(viewPort)
        if (scale>2){
            for (marker in markers) {
                // use the translator to translate and scale to the correct position on the TileView's coordinate system
                val adaptedX = marker.x * scale
                val adaptedY = marker.y * scale
                val left = adaptedX - MARKER_SIZE
                val top = adaptedY - MARKER_SIZE
                val right = adaptedX + MARKER_SIZE
                val bottom = adaptedY + MARKER_SIZE
                val markerBounds = RectF(left, top, right, bottom)

                //val originalMarkerBounds = RectF(marker.x-MARKER_SIZE,marker.y-MARKER_SIZE,marker.x+MARKER_SIZE,marker.y+MARKER_SIZE)
                // don't draw if outside the current display viewport
                if(viewPort.intersects(left,top,right,bottom)){
                    println("marker: " + markerBounds)
                    canvas.drawBitmap(marker.bitmap, null, markerBounds, null)
                    counter++
                }

            }

        }
        println("counter: " + counter)
    }

    fun addMarker(marker: MyMarker) {
        markers.add(marker)
        invalidate()
    }

    override fun onZoomChanged(zoom: Int, previous: Int) {}
    override fun onScaleChanged(scale: Float, previous: Float) {
        this.scale = scale
        invalidate()
    }
    override fun onScrollChanged(x: Int, y: Int) {
        this.x = x
        this.y = y
        invalidate()
    }


}
