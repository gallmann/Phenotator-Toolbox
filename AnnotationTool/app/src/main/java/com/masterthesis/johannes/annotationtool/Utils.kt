package com.masterthesis.johannes.annotationtool

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.support.v4.content.ContextCompat
import android.support.v4.graphics.drawable.DrawableCompat
import android.view.ViewConfiguration
import android.provider.MediaStore
import android.provider.DocumentsContract
import java.lang.Exception


val SHARED_PREFERENCES_KEY = "Shared_Preferences_Key"
public val LAST_OPENED_IMAGE_URI = "imageURI"



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

fun getRealPathFromURI(uri: Uri, context: Context): String {
    var filePath = ""
    val wholeID = DocumentsContract.getDocumentId(uri)

    // Split at colon, use second item in the array
    val id = wholeID.split(":".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()[1]

    val column = arrayOf(MediaStore.Images.Media.DATA)

    // where id is equal to
    val sel = MediaStore.Images.Media._ID + "=?"

    val cursor = context.contentResolver.query(
        MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
        column, sel, arrayOf(id), null
    )

    val columnIndex = cursor.getColumnIndex(column[0])

    if (cursor.moveToFirst()) {
        filePath = cursor.getString(columnIndex)
    }
    cursor.close()
    return filePath
}


fun createAnnotationFilePath(imagePath: String): String{
    if(imagePath.endsWith(".png") || imagePath.endsWith(".jpg")){
        return imagePath.dropLast(4).plus("_annotations.json")
    }

    throw Exception("File is not an Image of .png or .jpg Format")
}

fun uriToPath(uri: Uri): String{

    return uri.path.substringAfter(":")
}



