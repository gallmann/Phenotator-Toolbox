package com.masterthesis.johannes.annotationtool

import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import com.davemorrissey.labs.subscaleview.SubsamplingScaleImageView
import android.graphics.PointF
import android.graphics.Bitmap
import android.location.Location
import android.os.Handler
import androidx.core.content.ContextCompat
import android.view.MotionEvent
import android.view.View
import android.widget.LinearLayout
import com.davemorrissey.labs.subscaleview.ImageSource
import com.davemorrissey.labs.subscaleview.ImageViewState


class MyImageView constructor(context: Context?, var annotationState: AnnotationState, attr: AttributeSet? = null, var stateToRestore: ImageViewState? = null) :
    SubsamplingScaleImageView(context, attr) {

    private lateinit var pin: Bitmap
    private lateinit var locationPin: Bitmap
    var ZOOM_THRESH: Float = 0.9F
    lateinit var blinkingAnimation: Runnable

    private var showCurrentFlower: Boolean = true
    private var userLocation: Location? = null

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
        var w = density / 200f * pin.width
        var h = density / 200f * pin.height
        pin = Bitmap.createScaledBitmap(pin, w.toInt(), h.toInt(), true)

        locationPin = getBitmapFromVectorDrawable(context,R.drawable.my_location)
        w = density / 200f * locationPin.width
        h = density / 200f * locationPin.height
        locationPin = Bitmap.createScaledBitmap(locationPin, w.toInt(), h.toInt(), true)



        setBlinkingAnimation()
        setImage(ImageSource.uri(annotationState.imagePath), stateToRestore)
        maxScale = getValueFromPreferences(DEFAULT_MAX_ZOOM_VALUE,context)
        ZOOM_THRESH = getValueFromPreferences(DEFAULT_ANNOTATION_SHOW_VALUE,context)
    }

    fun reload(annotationState: AnnotationState, mainFragment: MainFragment){
        this.annotationState = annotationState
        setImage(ImageSource.uri(annotationState.imagePath))
        maxScale = getValueFromPreferences(DEFAULT_MAX_ZOOM_VALUE,context)
        ZOOM_THRESH = getValueFromPreferences(DEFAULT_ANNOTATION_SHOW_VALUE,context)
    }

    fun clickedOnExistingMark(x: Float, y: Float):Flower?{
        val w: Float = pin!!.width / 2F
        for((index,flower) in annotationState.annotatedFlowers.withIndex()){
            val sourceCoord = sourceToViewCoord(flower.getXPos(),flower.getYPos())
            val xPos = sourceCoord!!.x
            val yPos = sourceCoord!!.y
            val rect: RectF = RectF(xPos-w,yPos-w,xPos+w, yPos+w)
            if(rect.contains(x,y)){
                return flower
            }
        }
        return null
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // Don't draw pin before image is ready so it doesn't move around during setup.
        if (!isReady) {
            return
        }
        bringToFront()



        //DRAW USER POSITION
        if(userLocation != null){
            var tlLat = annotationState.getTopLeftCoordinates().first
            var tlLon = annotationState.getTopLeftCoordinates().second
            var brLat = annotationState.getBottomRightCoordinates().first
            var brLon = annotationState.getBottomRightCoordinates().second
            var uLon = userLocation!!.longitude
            var uLat = userLocation!!.latitude
            var imageWidth = sWidth
            var imageHeight = sHeight
            //println("width: $imageWidth height: $imageHeight")
            var userX = imageWidth*(uLon-tlLon)/(brLon-tlLon);
            var userY = imageHeight-imageHeight*(uLat-brLat)/(tlLat-brLat);

            if(userX < imageWidth && userX >= 0 && userY < imageHeight && userY >= 0){
                val paint = Paint()
                val filter = PorterDuffColorFilter(ContextCompat.getColor(context, R.color.Blue), PorterDuff.Mode.SRC_IN)
                paint.colorFilter = filter
                drawPin(userX.toFloat(), userY.toFloat(),canvas,paint,locationPin)
            }
        }


        //DRAW FLOWER ANNOTATIONS
        if(scale<ZOOM_THRESH) return

        if(showCurrentFlower && annotationState.currentFlower != null){
            var flower = annotationState.currentFlower!!
            drawPin(flower.getXPos(), flower.getYPos(),canvas,annotationState.getFlowerColor(flower.name,context), pin)
        }


        for((index,flower) in annotationState.annotatedFlowers.withIndex()){
            drawPin(flower.getXPos(), flower.getYPos(),canvas,annotationState.getFlowerColor(flower.name,context), pin)
        }
    }

    private fun drawPin(xPos: Float, yPos: Float, canvas: Canvas, color: Paint, pin: Bitmap){
        var viewcoord: PointF = sourceToViewCoord(xPos, yPos)!!

        if(isCoordinateVisible(canvas,viewcoord.x,viewcoord.y,pin!!.width / 2F)){
            val vX = viewcoord.x - pin!!.width / 2
            val vY = viewcoord.y - pin!!.height / 2
            canvas.drawBitmap(pin, vX, vY, color)
        }

    }

    private fun setBlinkingAnimation() {
        blinkingAnimation = object : Runnable {
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
        }
        postDelayed(blinkingAnimation, 300)
    }

    fun updateLocation(location: Location){
        this.userLocation = location
        invalidate()
    }

    fun isEditable(): Boolean{
        if(isReady && scale >= ZOOM_THRESH){
            return true
        }
        return false
    }

    override fun recycle() {
        super.recycle()
        removeCallbacks(blinkingAnimation)
    }

}
