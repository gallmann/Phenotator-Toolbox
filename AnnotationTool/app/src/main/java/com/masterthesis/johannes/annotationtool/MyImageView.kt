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
import ru.dimorinny.floatingtextbutton.FloatingTextButton

/*
class MyImageView constructor(context: Context?, var annotationState: AnnotationState,
                              var rightButton: FloatingTextButton,
                              var leftButton: FloatingTextButton,
                              var topButton: FloatingTextButton,
                              var bottomButton: FloatingTextButton,
                              attr: AttributeSet? = null,
                              var stateToRestore: ImageViewState? = null) :
    SubsamplingScaleImageView(context, attr) {

    private lateinit var pin: Bitmap
    private lateinit var polygonPin: Bitmap
    private lateinit var locationPin: Bitmap
    var ZOOM_THRESH: Float = 0.9F
    lateinit var blinkingAnimation: Runnable
    var currentEditIndex: Int = 0


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

        polygonPin = getBitmapFromVectorDrawable(context,R.drawable.point_image)
        w = density / 400f * polygonPin.width
        h = density / 400f * polygonPin.height
        polygonPin = Bitmap.createScaledBitmap(polygonPin, w.toInt(), h.toInt(), true)


        locationPin = getBitmapFromVectorDrawable(context,R.drawable.my_location)
        w = density / 200f * locationPin.width
        h = density / 200f * locationPin.height
        locationPin = Bitmap.createScaledBitmap(locationPin, w.toInt(), h.toInt(), true)



        setBlinkingAnimation()
        setImage(ImageSource.uri(annotationState.imageUri), stateToRestore)
        maxScale = getValueFromPreferences(DEFAULT_MAX_ZOOM_VALUE,context)
        ZOOM_THRESH = getValueFromPreferences(DEFAULT_ANNOTATION_SHOW_VALUE,context)
    }

    fun clickedOnExistingMark(x: Float, y: Float):Pair<Flower,Int>?{
        val w: Float = pin!!.width / 2F

        //CHECK CURRENT FLOWER
        if(annotationState.currentFlower != null){
            val flower: Flower = annotationState.currentFlower!!
            for(i in 0..flower.polygon.size-1) {
                val sourceCoord = sourceToViewCoord(flower.getXPos(i), flower.getYPos(i))
                val xPos = sourceCoord!!.x
                val yPos = sourceCoord!!.y
                val rect: RectF = RectF(xPos - w, yPos - w, xPos + w, yPos + w)
                if (rect.contains(x, y)) {
                    return Pair(flower, i)
                }
            }
        }



        //CHECK ALL ANNOTATIONS IN STATE
        for((index,flower) in annotationState.annotatedFlowers.withIndex()){
            for(i in 0..flower.polygon.size-1){
                val sourceCoord = sourceToViewCoord(flower.getXPos(i),flower.getYPos(i))
                val xPos = sourceCoord!!.x
                val yPos = sourceCoord!!.y
                val rect: RectF = RectF(xPos-w,yPos-w,xPos+w, yPos+w)
                if(rect.contains(x,y)){
                    return Pair(flower,i)
                }
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


        //ACTIVATE "NEXT TILE" BUTTONS IF NECESSARY!
        var topLeftCoord: PointF = viewToSourceCoord(0F,0F)!!
        var bottomRightCoord: PointF = viewToSourceCoord(canvas.width.toFloat(),canvas.height.toFloat())!!

        activateButtons(topLeftCoord, bottomRightCoord)



        //DRAW FLOWER ANNOTATIONS
        if(scale<ZOOM_THRESH) return

        if(annotationState.currentFlower != null){
            var flower = annotationState.currentFlower!!
            if(flower.isPolygon){
                drawPolygon(flower, canvas, true)
            }
            else{
                drawFlower(flower, canvas, true)
            }
        }


        for(flower in annotationState.annotatedFlowers){
            if(flower.isPolygon){
                drawPolygon(flower, canvas)
            }
            else{
                drawFlower(flower, canvas)
            }
        }
    }

    private fun drawFlower(flower: Flower, canvas: Canvas, isCurrentFlower: Boolean = false){
        if((isCurrentFlower && showCurrentFlower) || !isCurrentFlower){
            var color = annotationState.getFlowerColor(flower.name,context)
            drawPin(flower.getXPos(),flower.getYPos(),canvas,color,pin)
        }
    }

    private fun drawPolygon(flower: Flower, canvas: Canvas, isCurrentFlower: Boolean = false){
        var color = annotationState.getFlowerColor(flower.name,context)
        color.setStrokeWidth(polygonPin!!.width.toFloat() / 10);

        for(i in 0..flower.polygon.size-1){
            val nextPos = (i + 1) % flower.polygon.size


            if(isCurrentFlower && !showCurrentFlower && i == currentEditIndex){
                continue
            }
            var currViewCoord: PointF = sourceToViewCoord(flower.getXPos(i), flower.getYPos(i))!!
            var nextViewCoord: PointF = sourceToViewCoord(flower.getXPos(nextPos), flower.getYPos(nextPos))!!

            if(isCoordinateVisible(canvas,currViewCoord.x,currViewCoord.y,polygonPin!!.width / 2F) ||
                isCoordinateVisible(canvas,nextViewCoord.x,nextViewCoord.y,polygonPin!!.width / 2F)) {
                if(!(isCurrentFlower && !showCurrentFlower && nextPos == currentEditIndex)) {
                    canvas.drawLine(currViewCoord.x, currViewCoord.y, nextViewCoord.x, nextViewCoord.y, color)
                }
                val vX = currViewCoord.x - polygonPin!!.width / 2
                val vY = currViewCoord.y - polygonPin!!.height / 2
                canvas.drawBitmap(polygonPin, vX, vY, color)
            }
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

    fun activateButtons(topLeftCoord: PointF, bottomRightCoord: PointF){
        if(topLeftCoord.x <= 0 && annotationState.hasLeftNeighbour){
            leftButton!!.visibility = View.VISIBLE
        }
        else{
            leftButton!!.visibility = View.INVISIBLE
        }

        if(topLeftCoord.y <= 0 && annotationState.hasTopNeighbour){
            topButton!!.visibility = View.VISIBLE
        }
        else{
            topButton!!.visibility = View.INVISIBLE
        }

        if(bottomRightCoord.x >= sWidth && annotationState.hasRightNeighbour){
            rightButton.visibility = View.VISIBLE
        }
        else{
            rightButton.visibility = View.INVISIBLE
        }

        if(bottomRightCoord.y >= sHeight && annotationState.hasBottomNeighbour){
            bottomButton.visibility = View.VISIBLE
        }
        else{
            bottomButton.visibility = View.INVISIBLE
        }
    }

}
*/