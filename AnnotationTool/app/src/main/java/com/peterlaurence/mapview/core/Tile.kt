package com.peterlaurence.mapview.core

import android.graphics.Bitmap
import android.graphics.Paint

/**
 * A [Tile] is defined by its coordinates in the "pyramid". But a [Tile] is sub-sampled when the
 * scale becomes lower than the scale of the lowest level. To reflect that, there is [subSample]
 * property which is a positive integer (can be 0). If [subSample] is equal to 0, it means that the
 * [bitmap] of the tile is full scale. If [subSample] is 1, the [bitmap] is sub-sampled and its size
 * is half the original bitmap (the one at the lowest level), and so on.
 */
data class Tile(val zoom: Int, val row: Int, val col: Int, val subSample: Int) {
    lateinit var bitmap: Bitmap
    var paint: Paint? = null
}

data class TileSpec(val zoom: Int, val row: Int, val col: Int, val subSample: Int = 0)

fun Tile.sameSpecAs(spec: TileSpec): Boolean {
    return zoom == spec.zoom && row == spec.row && col == spec.col && subSample == spec.subSample
}

fun Tile.samePositionAs(tile: Tile): Boolean {
    return zoom == tile.zoom && row == tile.row && col == tile.col
}