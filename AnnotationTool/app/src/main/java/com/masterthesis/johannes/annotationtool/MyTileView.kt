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

    lateinit var markersView: MyMarkersView

    constructor(context: Context,annotationState: AnnotationState) : super(context) {
        init(annotationState)
    }

    private fun init(annotationState: AnnotationState) {
        markersView = MyMarkersView(context,this,annotationState)
        addView(markersView) // added before the callout view
    }

}
