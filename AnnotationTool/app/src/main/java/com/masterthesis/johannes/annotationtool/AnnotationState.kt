package com.masterthesis.johannes.annotationtool

class AnnotationState() {

    var annotatedFlowers: ArrayList<Flower> = ArrayList()
    var currentFlower: Flower? = null
    var flowerList: ArrayList<String> = arrayListOf("Sonnenblume", "Löwenzahn", "bla", "blm", "b", "hhh", "hf", "fhewf")
    var flowerCount: MutableMap<String,Int> = HashMap<String,Int>()
    var favs: ArrayList<String> = ArrayList<String>()

    init{
        for(s: String in flowerList){
            flowerCount[s] = 0
        }
    }

    private fun updateFavourites(){
        var favourites: ArrayList<String> = ArrayList<String>()
        flowerCount.toList()
            .sortedBy { (key, value) -> -value }
            .toMap()

        for((key,value) in flowerCount){
            if(value >0 && favourites.size < 5){
                favourites.add(key)
            }
        }
        favs = favourites
    }

    public fun isSelected(flowerName: String): Boolean{
        if(flowerName.equals(currentFlower!!.name)){
            return true
        }
        return false
    }

    public fun isSelected(index: Int): Boolean{
        if(flowerList[index].equals(currentFlower!!.name)){
            return true
        }
        return false
    }

    public fun selectFlower(index: Int){
        currentFlower!!.name = flowerList[index]
    }

    public fun selectFlower(name: String){
        currentFlower!!.name = name
    }

    public fun addNewFlowerMarker(x: Float, y: Float){
        var label: String = flowerList[0]
        if(favs.size >0){
            label = favs[0]
        }
        currentFlower = Flower(label, x,y)
        annotatedFlowers.add(currentFlower!!)
    }



}