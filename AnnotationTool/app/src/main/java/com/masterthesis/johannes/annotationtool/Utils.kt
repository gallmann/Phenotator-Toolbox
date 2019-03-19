package com.masterthesis.johannes.annotationtool

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.net.Uri
import android.os.Build
import android.os.Environment
import androidx.core.content.ContextCompat
import androidx.core.graphics.drawable.DrawableCompat
import android.view.ViewConfiguration
import java.lang.Exception


val SHARED_PREFERENCES_KEY = "Shared_Preferences_Key"
val LAST_OPENED_IMAGE_URI = "imageURI"
val USER_FLOWER_LIST = Pair(mutableSetOf("Sonnenblume", "Löwenzahn"),"flowerListKey")

val DEFAULT_MAX_ZOOM_VALUE = Pair(30F,"MAX_ZOOM_KEY")
val DEFAULT_ANNOTATION_SHOW_VALUE = Pair(0.9F,"ANNOTATION_SHOW_KEY")
val LOCATION_PERMISSION_REQUEST = 349
val TURN_ON_LOCATION_USER_REQUEST = 347
val CURRENT_FRAGMENT_KEY = "currentFragment"


public fun getBitmapFromVectorDrawable(context: Context, drawableId: Int): Bitmap {
    var drawable = ContextCompat.getDrawable(context, drawableId)
    if (Build.VERSION.SDK_INT < Build.VERSION_CODES.LOLLIPOP) {
        drawable = DrawableCompat.wrap(drawable!!).mutate()
    }

    val bitmap = Bitmap.createBitmap(
        drawable!!.intrinsicWidth,
        drawable.intrinsicHeight, Bitmap.Config.ARGB_8888
    )
    val canvas = Canvas(bitmap)
    drawable.setBounds(0, 0, canvas.width, canvas.height)
    drawable.draw(canvas)

    return bitmap
}


public fun isAClick(startX: Float, endX: Float, startY: Float, endY: Float, startTime: Long, endTime: Long, context: Context): Boolean {

    val MAX_CLICK_DURATION = ViewConfiguration.getTapTimeout()

    if(endTime-startTime > MAX_CLICK_DURATION){
        return false
    }

    val CLICK_ACTION_THRESHOLD = ViewConfiguration.get(context).getScaledTouchSlop()
    val differenceX = Math.abs(startX - endX)
    val differenceY = Math.abs(startY - endY)
    return !(differenceX > CLICK_ACTION_THRESHOLD || differenceY > CLICK_ACTION_THRESHOLD)
}

public fun isCoordinateVisible(canvas: Canvas, x: Float, y:Float, margin: Float): Boolean{
    if(x < 0 - margin || y < 0-margin){
        return false
    }
    if(x>canvas.width+margin || y > canvas.height+margin){
        return false
    }
    return true
}

fun isExternalStorageWritable(): Boolean {
    return Environment.getExternalStorageState() == Environment.MEDIA_MOUNTED
}


fun createAnnotationFilePath(imagePath: String): String{
    if(imagePath.endsWith(".png") || imagePath.endsWith(".jpg")){
        return imagePath.dropLast(4).plus("_annotations.json")
    }

    throw Exception("File is not an Image of .png or .jpg Format")
}

fun createGeoInfoFilePath(imagePath: String): String{
    if(imagePath.endsWith(".png") || imagePath.endsWith(".jpg")){
        return imagePath.dropLast(4).plus("_geoinfo.json")
    }

    throw Exception("File is not an Image of .png or .jpg Format")
}


fun uriToPath(uri: Uri): String{

    return uri.path.substringAfter(":")
}

fun getValueFromPreferences(id: Pair<Float,String>, context: Context): Float{
    val prefs = context.getSharedPreferences(SHARED_PREFERENCES_KEY, Context.MODE_PRIVATE)
    val restoredValue = prefs.getFloat(id.second,id.first)
    return restoredValue
}
fun setValueToPreferences(id: Pair<Float,String>, value: Float, context: Context){
    val editor = context.getSharedPreferences(SHARED_PREFERENCES_KEY, Context.MODE_PRIVATE).edit()
    editor.putFloat(id.second,value)
    editor.apply()
}
fun putFlowerListToPreferences(items:MutableList<String>, context: Context){
    val editor = context.getSharedPreferences(SHARED_PREFERENCES_KEY, Context.MODE_PRIVATE).edit()
    editor.putStringSet(USER_FLOWER_LIST.second,items.toMutableSet())
    editor.commit()
}
fun getFlowerListFromPreferences(context:Context):MutableList<String>{
    val prefs = context!!.getSharedPreferences(SHARED_PREFERENCES_KEY, Context.MODE_PRIVATE)
    val restoredValue = prefs.getStringSet(USER_FLOWER_LIST.second, USER_FLOWER_LIST.first)
    var items = restoredValue.toMutableList()
    items = items.sortedWith(compareBy(String.CASE_INSENSITIVE_ORDER, { it })).toMutableList()
    return items
}



