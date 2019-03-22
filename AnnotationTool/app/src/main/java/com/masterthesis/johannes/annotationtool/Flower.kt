package com.masterthesis.johannes.annotationtool

import java.lang.Exception
import java.lang.IndexOutOfBoundsException

class Flower(name: String, xPos: Float, yPos: Float) {
    var name: String = name
    var polygon: MutableList<Coord> = mutableListOf(Coord(xPos,yPos))
    var isPolygon: Boolean = false


    fun setXPos(x:Float){
        polygon[0].x = x
    }
    fun setYPos(y:Float){
        polygon[0].y = y
    }
    fun getXPos():Float{
        return polygon[0].x
    }
    fun getYPos():Float{
        return polygon[0].y
    }
    fun setXPos(x:Float, pos:Int){
        if(polygon.size > pos) polygon[pos].x = x
        else throw IndexOutOfBoundsException()
    }
    fun setYPos(y:Float,pos:Int){
        if(polygon.size > pos) polygon[pos].y = y
        else throw IndexOutOfBoundsException()
    }
    fun getXPos(pos:Int):Float{
        if(polygon.size > pos) return polygon[pos].x
        else throw IndexOutOfBoundsException()
    }
    fun getYPos(pos:Int):Float{
        if(polygon.size > pos) return polygon[pos].y
        else throw IndexOutOfBoundsException()
    }

    fun addPolygonPoint(coord: Coord){
        polygon.add(coord)
    }

    fun removePolygonPointAt(pos:Int){
        if(polygon.size > 1 && polygon.size > pos){
            polygon.removeAt(pos)
        }
    }
    fun removeLastPolygonPoint(){
        if(polygon.size > 1){
            polygon.removeAt(polygon.size-1)
        }
    }
    fun editPolygonPointAt(pos:Int,coord:Coord){
        if(polygon.size > pos){
            polygon[pos] = coord
        }
    }

    fun incrementXPos(){
        polygon[0].x++
    }
    fun incrementYPos(){
        polygon[0].y++
    }
    fun decrementXPos(){
        polygon[0].x--
    }
    fun decrementYPos(){
        polygon[0].y--
    }

    fun incrementXPos(pos:Int){
        if(polygon.size > pos) polygon[pos].x++
        else throw IndexOutOfBoundsException()
    }
    fun incrementYPos(pos:Int){
        if(polygon.size > pos) polygon[pos].y++
        else throw IndexOutOfBoundsException()
    }
    fun decrementXPos(pos:Int){
        if(polygon.size > pos) polygon[pos].x--
        else throw IndexOutOfBoundsException()
    }
    fun decrementYPos(pos:Int){
        if(polygon.size > pos) polygon[pos].y--
        else throw IndexOutOfBoundsException()
    }

    fun deletePolygon(){
        while (polygon.size > 1){
            polygon.removeAt(1)
        }
    }



}