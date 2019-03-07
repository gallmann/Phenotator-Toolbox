package com.masterthesis.johannes.annotationtool

import android.app.Activity
import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.ImageView
import android.widget.TextView

class FlowerListAdapter(var activity: Activity,
                        val annotationState: AnnotationState): BaseAdapter() {

    val inflater = activity?.getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater


    override fun getView(i: Int, view: View?, parent: ViewGroup?): View {
        val numberOfFavourites: Int = annotationState.favs.size
        if(i == 0 || i == numberOfFavourites+1){
            val rowView = inflater.inflate(R.layout.section_separator_list_item, parent, false)
            val nameView: TextView = rowView.findViewById(R.id.lv_list_hdr)
            if(i == 0) nameView.text = "FAVOURITES"
            else nameView.text = "ALL"
            return rowView
        }

        val rowView = inflater.inflate(R.layout.flower_list_item, parent, false)
        val nameView: TextView = rowView.findViewById(R.id.flower_name)
        val checkmarkView: ImageView = rowView.findViewById<ImageView>(R.id.checkmark_icon_imageview)

        if(i<=numberOfFavourites){
            nameView.text = annotationState.favs[i-1]
            if(annotationState.isSelected(annotationState.favs[i-1])){
                checkmarkView.visibility = View.VISIBLE
            }
            else{
                checkmarkView.visibility = View.INVISIBLE
            }
        }
        else{
            val index:Int = i-numberOfFavourites-2
            nameView.text = annotationState.flowerList[index]
            if(annotationState.isSelected(index)){
                checkmarkView.visibility = View.VISIBLE
            }
            else{
                checkmarkView.visibility = View.INVISIBLE
            }
        }
        return rowView
    }


    override fun getItem(position: Int): Any {
        return annotationState.flowerList[position]
    }

    override fun getItemId(position: Int): Long {
        return position.toLong()
    }

    override fun getCount(): Int {
        return annotationState.flowerList.size
    }

    fun selectedIndex(i: Int) {
        val numberOfFavourites: Int = annotationState.favs.size
        if (i == 0 || i == numberOfFavourites + 1) return
        if (i <= numberOfFavourites) {
            annotationState.selectFlower(annotationState.favs[i-1])
        } else {
            annotationState.selectFlower(i-numberOfFavourites-2)
        }
        notifyDataSetChanged()
    }
}