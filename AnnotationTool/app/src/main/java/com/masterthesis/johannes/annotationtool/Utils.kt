package com.masterthesis.johannes.annotationtool

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.os.Build
import android.support.v4.content.ContextCompat
import android.support.v4.graphics.drawable.DrawableCompat
import android.view.ViewConfiguration


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

