package layout

import android.app.Activity
import android.content.Context
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.TextView
import com.masterthesis.johannes.annotationtool.*

class SettingsListAdapter(var activity: Activity): BaseAdapter() {

    val inflater = activity?.getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
    val number_of_settings: Int = 2

    override fun getView(i: Int, view: View?, parent: ViewGroup?): View {
        val rowView = inflater.inflate(R.layout.default_settings_list_cell, parent, false)
        when(i){
            0 -> {
                rowView.findViewById<TextView>(R.id.settingTitle).text = "Max Zoom"
                rowView.findViewById<TextView>(R.id.value_edit_text).text = getValueFromPreferences(DEFAULT_MAX_ZOOM_VALUE,activity).toString()
                rowView.findViewById<TextView>(R.id.value_edit_text).addTextChangedListener(object : TextWatcher {
                    override fun afterTextChanged(editable: Editable?) {}
                    override fun beforeTextChanged(p0: CharSequence?, p1: Int, p2: Int, p3: Int) {}
                    override fun onTextChanged(p0: CharSequence, p1: Int, p2: Int, p3: Int) {
                        try {
                            setValueToPreferences(DEFAULT_MAX_ZOOM_VALUE,p0.toString().toFloat(),activity)
                        }
                        catch (e: NumberFormatException){

                        }
                    }
                })
            }
            1 -> {
                rowView.findViewById<TextView>(R.id.settingTitle).text = "Show annotations at zoom level"
                rowView.findViewById<TextView>(R.id.settingDetails).text = "A value smaller than 10 may slow the App down"
                rowView.findViewById<TextView>(R.id.value_edit_text).text = getValueFromPreferences(DEFAULT_ANNOTATION_SHOW_VALUE, activity).toString()
                rowView.findViewById<TextView>(R.id.value_edit_text).addTextChangedListener(object : TextWatcher {
                    override fun afterTextChanged(editable: Editable?) {}
                    override fun beforeTextChanged(p0: CharSequence?, p1: Int, p2: Int, p3: Int) {}
                    override fun onTextChanged(p0: CharSequence, p1: Int, p2: Int, p3: Int) {
                        try {
                            setValueToPreferences(DEFAULT_ANNOTATION_SHOW_VALUE,p0.toString().toFloat(), activity)
                        }
                        catch (e: NumberFormatException){

                        }
                    }
                })
            }
        }
        return rowView
    }


    override fun getItem(position: Int): Any {
        return 0
    }


    override fun getItemId(position: Int): Long {
        return position.toLong()
    }

    override fun getCount(): Int {
        return number_of_settings
    }


}