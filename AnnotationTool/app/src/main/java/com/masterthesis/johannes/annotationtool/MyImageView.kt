package com.masterthesis.johannes.annotationtool

import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import com.davemorrissey.labs.subscaleview.SubsamplingScaleImageView
import android.graphics.PointF
import android.graphics.Bitmap
import android.net.Uri
import android.view.MotionEvent
import android.view.View
import android.widget.LinearLayout
import com.davemorrissey.labs.subscaleview.ImageSource


class MyImageView constructor(context: Context, val annotationState: AnnotationState, val mainFragment: MainFragment, attr: AttributeSet? = null) :
    SubsamplingScaleImageView(context, attr), View.OnTouchListener {

    private lateinit var pin: Bitmap
    private var ZOOM_THRESH: Float = 0.9F

    private var showCurrentFlower: Boolean = true
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
        setOnTouchListener(this)
        val density = resources.displayMetrics.densityDpi.toFloat()
        pin = getBitmapFromVectorDrawable(context,R.drawable.cross)
        val w = density / 200f * pin.width
        val h = density / 200f * pin.height
        pin = Bitmap.createScaledBitmap(pin, w.toInt(), h.toInt(), true)
        setBlinkingAnimation()
        setImage(ImageSource.uri(annotationState.imagePath))
        maxScale = getValueFromPreferences(DEFAULT_MAX_ZOOM_VALUE,context)
        ZOOM_THRESH = getValueFromPreferences(DEFAULT_ANNOTATION_SHOW_VALUE,context)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // Don't draw pin before image is ready so it doesn't move around during setup.
        if (!isReady || scale < ZOOM_THRESH) {
            return
        }

        if(showCurrentFlower && annotationState.currentFlower != null){
            var flower = annotationState.currentFlower!!
            var viewcoord: PointF = sourceToViewCoord(flower.xPos, flower.yPos)!!
            val vX = viewcoord.x - pin!!.width / 2
            val vY = viewcoord.y - pin!!.height / 2
            canvas.drawBitmap(pin, vX, vY, annotationState.getFlowerColor(flower.name,context))
        }


        for((index,flower) in annotationState.annotatedFlowers.withIndex()){
            var viewcoord: PointF = sourceToViewCoord(flower.xPos, flower.yPos)!!

            if(isCoordinateVisible(canvas,viewcoord.x,viewcoord.y,pin!!.width / 2F)){
                val vX = viewcoord.x - pin!!.width / 2
                val vY = viewcoord.y - pin!!.height / 2
                canvas.drawBitmap(pin, vX, vY, annotationState.getFlowerColor(flower.name,context))
            }
        }
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
                    if(isReady && scale >= ZOOM_THRESH){
                        val editFlower = clickedOnExistingMark(endX,endY);
                        if(editFlower != null){
                            editMark(editFlower)
                        }
                        else {
                            addNewMark(event)
                        }
                    }
                }
            }
        }
        return false
    }

    private fun clickedOnExistingMark(x: Float, y: Float):Flower?{
        val w: Float = pin!!.width / 2F
        for((index,flower) in annotationState.annotatedFlowers.withIndex()){
            val sourceCoord = sourceToViewCoord(flower.xPos,flower.yPos)
            val xPos = sourceCoord!!.x
            val yPos = sourceCoord!!.y
            val rect: RectF = RectF(xPos-w,yPos-w,xPos+w, yPos+w)
            if(rect.contains(x,y)){
                return flower
            }
        }
        return null
    }

    private fun setBlinkingAnimation() {
        postDelayed(object : Runnable {
            override fun run() {
                showCurrentFlower = !showCurrentFlower
                invalidate()
                if(showCurrentFlower){
                    postDelayed(this, 600)
                }
                else{
                    postDelayed(this, 200)
                }
            }
        }, 300)
    }


    private fun addNewMark(event: MotionEvent){
        var sourcecoord: PointF = viewToSourceCoord(PointF(event.x, event.y))!!
        annotationState.addNewFlowerMarker(sourcecoord.x, sourcecoord.y)
        mainFragment.updateFlowerListView()
        invalidate()
    }

    private fun editMark(flower: Flower){
        annotationState.startEditingFlower(flower)
        mainFragment.updateFlowerListView()
        invalidate()
    }


}
