package com.masterthesis.johannes.annotationtool

import androidx.recyclerview.widget.RecyclerView
import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.TextView
import com.google.android.material.snackbar.Snackbar
import android.content.Context
import android.view.View


class SettingsListAdapter(var items: MutableList<String>, val parentView: View, val context: Context) :
    RecyclerView.Adapter<SettingsListAdapter.MyViewHolder>() {

    class MyViewHolder(val textView: TextView) : RecyclerView.ViewHolder(textView)

    var mRecentlyDeletedItem: Pair<String, Int> = Pair("",0)

    override fun onCreateViewHolder(parent: ViewGroup,
                                    viewType: Int): SettingsListAdapter.MyViewHolder {
        val textView = LayoutInflater.from(parent.context)
            .inflate(android.R.layout.simple_list_item_1, parent, false) as TextView
        return MyViewHolder(textView)
    }

    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {
        holder.textView.text = items[position]
    }

    override fun getItemCount() = items.size

    fun deleteItem(position: Int) {
        mRecentlyDeletedItem = Pair(items.get(position), position);
        items.removeAt(position);
        putFlowerListToPreferences(items,context)
        notifyItemRemoved(position);
        showUndoSnackbar();
    }


    private fun showUndoSnackbar() {
        val snack: Snackbar = Snackbar.make(parentView, R.string.snackbar_item_deleted, Snackbar.LENGTH_LONG)
        snack.setAction(R.string.undo, View.OnClickListener {undoDelete()})
        snack.show()
    }

    private fun undoDelete() {
        items.add(mRecentlyDeletedItem.second,mRecentlyDeletedItem.first)
        notifyItemInserted(mRecentlyDeletedItem.second)
        putFlowerListToPreferences(items,context)
    }

    fun replaceItem(position: Int, new_item: String){
        items[position] = new_item;
        putFlowerListToPreferences(items,context)
        items = getFlowerListFromPreferences(context)
        notifyItemChanged(position);
        notifyItemMoved(position, items.indexOf(new_item))
    }


    fun insertItem(item:String){
        items.add(item)
        putFlowerListToPreferences(items,context)
        items = getFlowerListFromPreferences(context)
        notifyItemInserted(items.indexOf(item))
    }

    fun refresh(newItems: MutableList<String>){
        items = newItems
        notifyDataSetChanged()
    }
}

