package com.masterthesis.johannes.annotationtool

import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import com.davemorrissey.labs.subscaleview.SubsamplingScaleImageView
import android.graphics.PointF
import android.graphics.Bitmap
import android.support.v4.graphics.drawable.DrawableCompat
import android.os.Build
import android.support.v4.content.ContextCompat
import android.view.MotionEvent
import android.view.View
import android.view.ViewConfiguration
import android.widget.LinearLayout


class MyImageView constructor(context: Context, val annotationState: AnnotationState, val mainFragment: MainFragment, attr: AttributeSet? = null) :
    SubsamplingScaleImageView(context, attr), View.OnTouchListener {

    private val paint = Paint()
    private val vPin = PointF()
    private var sPin: PointF? = null
    private var pin: Bitmap? = null



    private var startTime: Long = 0
    private var startX: Float = 0.toFloat()
    private var startY: Float = 0.toFloat()

    init {
        initialise()
    }

    private fun initialise() {
        layoutParams = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.MATCH_PARENT
        )

        val density = resources.displayMetrics.densityDpi.toFloat()
        pin = getBitmapFromVectorDrawable(context,R.drawable.cross)

        val w = density / 10f * pin!!.width
        val h = density / 10f * pin!!.height
        pin = Bitmap.createScaledBitmap(pin!!, w.toInt(), h.toInt(), true)

    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        


    }

    override fun onTouch(imageView: View, event: MotionEvent): Boolean {

        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                startX = event.x
                startY = event.y
                startTime = System.currentTimeMillis()
            }
            MotionEvent.ACTION_UP -> {
                val endX = event.x
                val endY = event.y
                val endTime = System.currentTimeMillis()
                if (isAClick(startX, endX, startY, endY, startTime, endTime, context)) {
                    if(isReady){
                        addNewMark(event)
                    }
                }
            }
        }
        return false
    }


    private fun addNewMark(event: MotionEvent){
        var sourcecoord: PointF = viewToSourceCoord(PointF(event.x, event.y))!!
        annotationState.addNewFlowerMarker(sourcecoord.x, sourcecoord.y)
        mainFragment.updateFlowerListView()
        invalidate()
    }


}
