package com.masterthesis.johannes.annotationtool

import android.graphics.Paint
import android.graphics.PorterDuff
import android.graphics.PorterDuffColorFilter
import android.content.Context
import android.net.Uri
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.google.gson.stream.JsonReader
import java.io.*


class AnnotationState(var imageUri: Uri, val context: Context) {

    var annotatedFlowers: ArrayList<Flower> = ArrayList<Flower>()
    var currentFlower: Flower? = null
    var flowerList: ArrayList<String> = arrayListOf("Sonnenblume", "Löwenzahn", "bla", "blm", "b", "hhh", "hf", "fhewf")
    var flowerCount: MutableMap<String,Int> = HashMap<String,Int>()
    var favs: ArrayList<String> = ArrayList<String>()
    lateinit var annotationFileUri: Uri

    init{
        for(s: String in flowerList){
            flowerCount[s] = 0
        }
        // represent the path portion of the URL as a file
        val imageFile = File(imageUri.path)

        annotationFileUri = Uri.withAppendedPath(Uri.parse(imageFile.parent),imageFile.name.dropLast(4) + "_annotations.json")

        if(!isExternalStorageWritable()){
            throw Exception("External Storage is not Writable")
        }

        var annotationFile: File = File(annotationFileUri.path)
        if(annotationFile.exists()){

            val gson = Gson()
            val reader = JsonReader(FileReader(annotationFileUri.path))
            val myType = object : TypeToken<List<Flower>>() {}.type
            annotatedFlowers = ArrayList<Flower>(gson.fromJson<List<Flower>>(reader, myType))
        }
    }

    private fun saveToFile(){

        val gson = Gson()
        val jsonString = gson.toJson(annotatedFlowers);
        val fOut = FileOutputStream(File(annotationFileUri.path))
        val myOutWriter = OutputStreamWriter(fOut)
        myOutWriter.append(jsonString)
        myOutWriter.close()
        fOut.close()
    }

    private fun updateFavourites(){
        var favourites: ArrayList<String> = ArrayList<String>()
        var flowerCountSorted = flowerCount.toList()
            .sortedBy { (key, value) -> -value }
            .toMap()

        for((key,value) in flowerCountSorted){
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
        if(!currentFlower!!.name.equals(flowerList[index])){
            flowerCount[currentFlower!!.name] = flowerCount[currentFlower!!.name]!! - 1
            flowerCount[flowerList[index]] = flowerCount[flowerList[index]]!! + 1
            //updateFavourites()
        }
        currentFlower!!.name = flowerList[index]
    }

    public fun selectFlower(name: String){
        if(!currentFlower!!.name.equals(name)){
            flowerCount[currentFlower!!.name] = flowerCount[currentFlower!!.name]!! - 1
            flowerCount[name] = flowerCount[name]!! + 1
            //updateFavourites()
        }
        currentFlower!!.name = name
    }

    public fun addNewFlowerMarker(x: Float, y: Float){
        if(currentFlower != null){
            permanentlyAddCurrentFlower()
        }

        var label: String = flowerList[0]
        if(annotatedFlowers.size > 0){
            label = annotatedFlowers[annotatedFlowers.size-1].name
        }
        currentFlower = Flower(label, x,y)
        flowerCount[label] = flowerCount[label]!! + 1
    }

    public fun permanentlyAddCurrentFlower(){
        annotatedFlowers.add(currentFlower!!)
        updateFavourites()
        saveToFile()
        currentFlower = null
    }

    public fun cancelCurrentFlower(){
        flowerCount[currentFlower!!.name] = flowerCount[currentFlower!!.name]!! - 1
        currentFlower = null
    }

    public fun getFlowerColor(name: String, context: Context): Paint{
        val index = flowerList.indexOf(name)
        val ta = context.resources.obtainTypedArray(R.array.colors)
        val paint = Paint()
        val filter = PorterDuffColorFilter(ta.getColor(index%ta.length(),0), PorterDuff.Mode.SRC_IN)
        paint.colorFilter = filter
        ta.recycle()
        return paint
    }

    public fun startEditingFlower(flower: Flower){
        if(currentFlower != null){
            cancelCurrentFlower()
        }

        if(annotatedFlowers.contains(flower)){
            currentFlower = flower
            annotatedFlowers.remove(flower)
            saveToFile()
        }
        else{
            throw Exception("Wrooong! The flower must be in the ArrayList! Believe me!")
        }
    }

}