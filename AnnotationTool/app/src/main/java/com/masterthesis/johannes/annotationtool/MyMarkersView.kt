package com.masterthesis.johannes.annotationtool

import android.graphics.Canvas.EdgeType
import android.R.attr.y
import android.R.attr.x
import android.content.Context
import android.graphics.*
import android.location.Location
import android.view.View
import androidx.core.content.ContextCompat
import com.moagrius.tileview.TileView


class MyMarkersView(context: Context, var tileView:MyTileView, var annotationState: AnnotationState) : View(context), TileView.Listener {


    private var y = 0
    private var x = 0
    private var scale = 1f

    private var locationPin:Bitmap
    private var pin:Bitmap
    private var polygonPin:Bitmap

    lateinit var blinkingAnimation: Runnable
    private var showCurrentFlower: Boolean = true
    var ZOOM_THRESH: Float = 0.9F

    var currentEditIndex: Int = 0

    private var userLocation: Location? = null



    init {
        tileView.addListener(this)
        val density = resources.displayMetrics.densityDpi.toFloat()

        locationPin = getBitmapFromVectorDrawable(context,R.drawable.my_location)

        var w = density / 200f * locationPin.width
        var h = density / 200f * locationPin.height
        locationPin = Bitmap.createScaledBitmap(locationPin, w.toInt(), h.toInt(), true)

        pin = getBitmapFromVectorDrawable(context,R.drawable.cross)

        w = density / 200f * pin.width
        h = density / 200f * pin.height
        pin = Bitmap.createScaledBitmap(pin, w.toInt(), h.toInt(), true)

        polygonPin = getBitmapFromVectorDrawable(context,R.drawable.point_image)

        w = density / 400f * polygonPin.width
        h = density / 400f * polygonPin.height
        polygonPin = Bitmap.createScaledBitmap(polygonPin, w.toInt(), h.toInt(), true)
        setBlinkingAnimation()
        ZOOM_THRESH = getValueFromPreferences(DEFAULT_ANNOTATION_SHOW_VALUE,context)

    }

    override protected fun onDraw(canvas: Canvas) {


        var viewPort = RectF(x.toFloat(),y.toFloat(),(x+tileView.width).toFloat(),(y+tileView.height).toFloat())

        //DRAW USER POSITION
        if(userLocation != null){
            var tlLat = annotationState.getTopLeftCoordinates().first
            var tlLon = annotationState.getTopLeftCoordinates().second
            var brLat = annotationState.getBottomRightCoordinates().first
            var brLon = annotationState.getBottomRightCoordinates().second
            var uLon = userLocation!!.longitude
            var uLat = userLocation!!.latitude
            var imageWidth = annotationState.getImageWidth()
            var imageHeight = annotationState.getImageHeight()
            //println("width: $imageWidth height: $imageHeight")
            var userX = imageWidth*(uLon-tlLon)/(brLon-tlLon);
            var userY = imageHeight-imageHeight*(uLat-brLat)/(tlLat-brLat);

            if(userX < imageWidth && userX >= 0 && userY < imageHeight && userY >= 0){
                val paint = Paint()
                val filter = PorterDuffColorFilter(ContextCompat.getColor(context, R.color.Blue), PorterDuff.Mode.SRC_IN)
                paint.colorFilter = filter
                drawPin(userX.toFloat(), userY.toFloat() ,viewPort, canvas, paint, locationPin)
            }
        }





        if(scale<ZOOM_THRESH) return


        if(annotationState.currentFlower != null){
            var flower = annotationState.currentFlower!!
            if(flower.isPolygon){
                drawPolygon(flower, canvas, viewPort, true)
            }
            else{
                drawFlower(flower, canvas, viewPort, true)
            }
        }

        for(flower in annotationState.annotatedFlowers){
            if(flower.isPolygon){
                drawPolygon(flower, canvas,viewPort)
            }
            else{
                drawFlower(flower, canvas,viewPort)
            }
        }

    }


    fun isEditable(): Boolean{
        if(scale >= ZOOM_THRESH){
            return true
        }
        return false
    }

    fun clickedOnExistingMark(x: Float, y: Float):Pair<Flower,Int>?{

        var cc = convertCoordinates(x,y)
        cc.x = cc.x*scale
        cc.y = cc.y*scale


        //CHECK CURRENT FLOWER
        if(annotationState.currentFlower != null){
            val flower: Flower = annotationState.currentFlower!!
            for(i in 0..flower.polygon.size-1) {
                var markerBounds = getMarkerBounds(flower.getXPos(i), flower.getYPos(i),pin)
                if (markerBounds.contains(cc.x, cc.y)) {
                    return Pair(flower, i)
                }
            }
        }

        //CHECK ALL ANNOTATIONS IN STATE
        for((index,flower) in annotationState.annotatedFlowers.withIndex()){
            for(i in 0..flower.polygon.size-1){
                var markerBounds = getMarkerBounds(flower.getXPos(i), flower.getYPos(i),pin)
                if (markerBounds.contains(cc.x, cc.y)) {
                    return Pair(flower,i)
                }
            }
        }
        return null
    }

    fun updateLocation(location: Location){
        this.userLocation = location
        invalidate()
    }

    private fun drawPolygon(flower: Flower, canvas: Canvas,viewPort:RectF, isCurrentFlower: Boolean = false){
        var color = annotationState.getFlowerColor(flower.name,context)
        color.setStrokeWidth(polygonPin!!.width.toFloat() / 10);

        for(i in 0..flower.polygon.size-1){
            val nextPos = (i + 1) % flower.polygon.size


            if(isCurrentFlower && !showCurrentFlower && i == currentEditIndex){
                continue
            }

            if(!(isCurrentFlower && !showCurrentFlower && nextPos == currentEditIndex)) {
                drawLine(flower.getXPos(i), flower.getYPos(i), flower.getXPos(nextPos), flower.getYPos(nextPos), canvas, viewPort, color)
            }
            drawPin(flower.getXPos(i),flower.getYPos(i),viewPort,canvas,color,polygonPin)

        }
    }

    private fun getMarkerBounds(x:Float,y:Float, pin:Bitmap):RectF{
        var scaledX = x*scale
        var scaledY = y*scale
        val left = scaledX - pin!!.width / 2
        val top = scaledY - pin!!.height / 2
        val right = scaledX + pin!!.width / 2
        val bottom = scaledY + pin!!.height / 2
        val markerBounds = RectF(left, top, right, bottom)
        return markerBounds
    }

    private fun drawFlower(flower: Flower, canvas: Canvas, viewPort:RectF, isCurrentFlower: Boolean = false){
        if((isCurrentFlower && showCurrentFlower) || !isCurrentFlower){
            var color = annotationState.getFlowerColor(flower.name,context)
            drawPin(flower.getXPos(),flower.getYPos(), viewPort, canvas,color,pin)
        }
    }

    private fun drawLine(xStart:Float,yStart:Float,xEnd:Float,yEnd:Float, canvas:Canvas,viewPort:RectF, color:Paint){
        if(RectF.intersects(viewPort,getMarkerBounds(xStart,yStart,pin))||RectF.intersects(viewPort,getMarkerBounds(xEnd,yEnd,pin)))
            canvas.drawLine(xStart*scale, yStart*scale, xEnd*scale, yEnd*scale, color)
    }

    private fun drawPin(xPos: Float, yPos: Float, viewPort:RectF, canvas: Canvas, color: Paint, pin: Bitmap){
        val markerBounds = getMarkerBounds(xPos,yPos, pin)
        if(RectF.intersects(viewPort,markerBounds)){
            canvas.drawBitmap(pin, null, markerBounds, color)
        }
    }

    fun convertCoordinates(x:Float,y:Float):Coord{
        var newX = this.x/scale + x/scale
        var newY = this.y/scale + y/scale
        return Coord(newX,newY)

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


}
