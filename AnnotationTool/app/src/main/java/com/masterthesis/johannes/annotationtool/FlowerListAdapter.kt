package com.masterthesis.johannes.annotationtool

import android.content.Context
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import java.nio.file.Files.size
import android.view.ViewGroup
import android.view.LayoutInflater
import android.view.View
import android.widget.ImageView
import com.simplecityapps.recyclerview_fastscroll.views.FastScrollRecyclerView


class FlowerListAdapter(context: Context, val annotationState: AnnotationState) :
    RecyclerView.Adapter<RecyclerView.ViewHolder>(), FastScrollRecyclerView.SectionedAdapter,
    FastScrollRecyclerView.MeasurableAdapter<RecyclerView.ViewHolder> {
    private val mInflater: LayoutInflater
    private var mClickListener: ItemClickListener? = null

    init {
        this.mInflater = LayoutInflater.from(context)
    }

    // inflates the row layout from xml when needed
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        val view = mInflater.inflate(viewType, parent, false)
        if(viewType == R.layout.section_separator_list_item){
            return HeaderViewHolder(view)
        }
        else{
            return FlowerViewHolder(view)
        }
    }

    override fun getItemViewType(position: Int): Int {
        val numberOfFavourites: Int = annotationState.favs.size
        if(position == 0 || position == numberOfFavourites+1) {
            return R.layout.section_separator_list_item
        }
        else{
            return R.layout.flower_list_item
        }
    }

    // binds the data to the TextView in each row
    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {

        when(holder){
            is HeaderViewHolder ->{
                if(position == 0) holder.headerTextView.text = "FAVOURITES"
                else holder.headerTextView.text = "ALL"
            }

            is FlowerViewHolder -> {
                val numberOfFavourites: Int = annotationState.favs.size

                if(position<=numberOfFavourites){
                    holder.flowerTextView.text = annotationState.favs[position-1] + " (" + annotationState.getFlowerCount(annotationState.favs[position-1]) + ")"
                    if(annotationState.isSelected(annotationState.favs[position-1])){
                        holder.checkmarkView.visibility = View.VISIBLE
                    }
                    else{
                        holder.checkmarkView.visibility = View.INVISIBLE
                    }
                }
                else{
                    val index:Int = position-numberOfFavourites-2
                    holder.flowerTextView.text = annotationState.flowerList[index] + " (" + annotationState.getFlowerCount(annotationState.flowerList[index]) + ")"
                    if(annotationState.isSelected(index)){
                        holder.checkmarkView.visibility = View.VISIBLE
                    }
                    else{
                        holder.checkmarkView.visibility = View.INVISIBLE
                    }
                }
            }
        }
    }

    // total number of rows
    override fun getItemCount(): Int {
        return annotationState.flowerList.size + 2 + annotationState.favs.size
    }

    override fun getViewTypeHeight(recyclerView: RecyclerView, viewHolder: RecyclerView.ViewHolder?, viewType: Int): Int {

        if(viewType == R.layout.section_separator_list_item){
            return recyclerView.getResources().getDimensionPixelSize(R.dimen.lvHdrItemHeight);
        }
        else {
            return recyclerView.getResources().getDimensionPixelSize(R.dimen.lvFlowerCellHeight);
        }
    }

    override fun getSectionName(position: Int): String {
        val numberOfFavourites: Int = annotationState.favs.size
        if(position <= numberOfFavourites+1) {
            return "*"
        }
        else{
            return annotationState.flowerList[position-annotationState.favs.size-2][0].toString().toUpperCase()
        }
    }

    // stores and recycles views as they are scrolled off screen
    inner class FlowerViewHolder internal constructor(itemView: View) : RecyclerView.ViewHolder(itemView), View.OnClickListener {
        internal var flowerTextView: TextView
        internal var checkmarkView: ImageView

        init {
            checkmarkView = itemView.findViewById(R.id.checkmark_icon_imageview)
            flowerTextView = itemView.findViewById(R.id.flower_name)
            itemView.setOnClickListener(this)
        }

        override fun onClick(view: View) {
            if (mClickListener != null) mClickListener!!.onItemClick(view, adapterPosition)
        }
    }

    inner class HeaderViewHolder internal constructor(itemView: View) : RecyclerView.ViewHolder(itemView), View.OnClickListener {
        internal var headerTextView: TextView

        init {
            headerTextView = itemView.findViewById(R.id.lv_list_hdr)
            itemView.setOnClickListener(this)
        }
        override fun onClick(view: View) {}
    }

    // convenience method for getting data at click position
    internal fun getItem(id: Int): String {
        return ""
    }

    // allows clicks events to be caught
    internal fun setClickListener(itemClickListener: ItemClickListener) {
        this.mClickListener = itemClickListener
    }

    // parent activity will implement this method to respond to click events
    interface ItemClickListener {
        fun onItemClick(view: View, position: Int)
    }


    fun selectedIndex(i: Int) {
        val numberOfFavourites: Int = annotationState.favs.size
        if (i == 0 || i == numberOfFavourites + 1) return
        val selectedPosFavBefore = annotationState.favs.indexOf(annotationState.currentFlower!!.name)+1
        val selectedPosBefore = annotationState.flowerList.indexOf(annotationState.currentFlower!!.name) + 2 + annotationState.favs.size
        if (i <= numberOfFavourites) {
            annotationState.selectFlower(annotationState.favs[i-1])

        } else {
            annotationState.selectFlower(i-numberOfFavourites-2)
        }
        val selectedPosFavAfter = annotationState.favs.indexOf(annotationState.currentFlower!!.name)+1
        val selectedPosAfter = annotationState.flowerList.indexOf(annotationState.currentFlower!!.name) + 2 + annotationState.favs.size

        notifyItemChanged(selectedPosAfter)
        notifyItemChanged(selectedPosFavAfter)
        notifyItemChanged(selectedPosBefore)
        notifyItemChanged(selectedPosFavBefore)


    }
}
