package com.masterthesis.johannes.annotationtool

import android.R.attr.y
import android.R.attr.x
import android.content.Context
import android.graphics.Bitmap
import android.util.AttributeSet
import com.moagrius.tileview.TileView
import com.moagrius.tileview.plugins.CoordinatePlugin
import com.moagrius.tileview.plugins.MarkerPlugin
import com.moagrius.widget.ScalingScrollView


class MyTileView : TileView {

    private var markersView: MyMarkersView? = null

    constructor(context: Context) : super(context) {
        init()
    }

    constructor(context: Context, attrs: AttributeSet) : super(context, attrs) {
        init()
    }

    private fun init() {
        markersView = MyMarkersView(context,this)
        addView(markersView) // added before the callout view
    }



    fun addMarker(bitmap: Bitmap, x: Float, y: Float) {
        val marker = MyMarker()
        marker.x = x
        marker.y = y
        marker.bitmap = bitmap
        markersView!!.addMarker(marker)
    }

}
