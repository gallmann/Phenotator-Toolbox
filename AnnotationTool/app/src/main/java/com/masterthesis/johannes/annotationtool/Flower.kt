package com.masterthesis.johannes.annotationtool

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
    fun addPolygonPoint(coord: Coord){
        polygon.add(coord)
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

    fun incrementXPosAt(pos:Int){
        if(polygon.size > pos) polygon[pos].x++
    }
    fun incrementYPosAt(pos:Int){
        if(polygon.size > pos) polygon[pos].y++
    }
    fun decrementXPosAt(pos:Int){
        if(polygon.size > pos) polygon[pos].x--
    }
    fun decrementYPosAt(pos:Int){
        if(polygon.size > pos) polygon[pos].y--
    }

    fun deletePolygon(){
        for(i in polygon.size-1..1){
            polygon.removeAt(i)
        }
    }



}