package com.masterthesis.johannes.annotationtool

import android.R.attr.y
import android.R.attr.x
import android.content.Context
import android.graphics.Bitmap
import android.util.AttributeSet
import com.moagrius.tileview.TileView
import com.moagrius.tileview.plugins.CoordinatePlugin


class MyTileView : TileView {

    private var markersView: MyMarkersView? = null

    constructor(context: Context) : super(context) {
        init()
    }

    constructor(context: Context, attrs: AttributeSet) : super(context, attrs) {
        init()
    }

    private fun init() {
        markersView = MyMarkersView(context)
        addView(markersView) // added before the callout view
        var c:CoordinatePlugin = CoordinatePlugin(10.0,10.0,10.0,10.0)



        // ..... other code
    }

    fun addMarker(bitmap: Bitmap, x: Float, y: Float) {
        val marker = MyMarker()
        marker.x = x
        marker.y = y
        marker.bitmap = bitmap
        markersView!!.addMarker(marker)
    }

    // pass the current scale to the markers view
    fun onScaleChanged(scale: Float, previous: Float) {
        super.onScaleChanged(this,scale, previous)
        markersView!!.onScale(scale)
    }
}
