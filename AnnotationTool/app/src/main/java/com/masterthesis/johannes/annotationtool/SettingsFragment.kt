package com.masterthesis.johannes.annotationtool

import android.Manifest
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.text.Editable
import android.text.TextWatcher
import android.view.*
import androidx.recyclerview.widget.DividerItemDecoration
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.recyclerview.widget.ItemTouchHelper
import android.text.InputType
import android.webkit.MimeTypeMap
import android.widget.*
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader


class SettingsFragment : Fragment(), View.OnClickListener  {

    private var listener: OnFragmentInteractionListener? = null
    private lateinit var recyclerView: RecyclerView
    private lateinit var viewAdapter: SettingsListAdapter
    private lateinit var viewManager: RecyclerView.LayoutManager
    lateinit var max_zoom_cell: LinearLayout
    lateinit var annotation_zoom_cell: LinearLayout
    lateinit var items: MutableList<String>
    private val READ_PHONE_STORAGE_RETURN_CODE: Int = 1
    val READ_REQUEST_CODE: Int = 42

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setHasOptionsMenu(true)

    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Inflate the layout for this fragment
        val fragmentView: View = inflater.inflate(R.layout.fragment_settings, container, false)

        setupRecyclerView(fragmentView)
        setupMainSettings(fragmentView)




        return fragmentView
    }

    fun setupRecyclerView(fragmentView: View){
        items = getFlowerListFromPreferences(context!!)
        viewAdapter = SettingsListAdapter(items,fragmentView.findViewById(R.id.recycler_view_container), context!!)
        recyclerView = fragmentView.findViewById<RecyclerView>(R.id.flower_list_view).apply {
            setHasFixedSize(true)
        }
        recyclerView.addItemDecoration(
            DividerItemDecoration(
                recyclerView.context,
                DividerItemDecoration.VERTICAL
            )
        )
        recyclerView.adapter = viewAdapter
        recyclerView.layoutManager = LinearLayoutManager(context!!)
        val itemTouchHelper = ItemTouchHelper(SwipeToDeleteCallback(context!!,viewAdapter))
        itemTouchHelper.attachToRecyclerView(recyclerView)

        fragmentView.findViewById<Button>(R.id.add_button).setOnClickListener(this)
        fragmentView.findViewById<Button>(R.id.import_button).setOnClickListener(this)

    }

    fun setupMainSettings(fragmentView: View){
        max_zoom_cell = fragmentView.findViewById<LinearLayout>(R.id.max_zoom_cell)
        max_zoom_cell.findViewById<TextView>(R.id.settingTitle).text = resources.getString(R.string.max_zoom_title)
        max_zoom_cell.findViewById<TextView>(R.id.value_edit_text).text = getValueFromPreferences(DEFAULT_MAX_ZOOM_VALUE,context!!).toString()
        max_zoom_cell.findViewById<TextView>(R.id.value_edit_text).addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(editable: Editable?) {}
            override fun beforeTextChanged(p0: CharSequence?, p1: Int, p2: Int, p3: Int) {}
            override fun onTextChanged(p0: CharSequence, p1: Int, p2: Int, p3: Int) {
                try { setValueToPreferences(DEFAULT_MAX_ZOOM_VALUE,p0.toString().toFloat(),context!!) }
                catch (e: NumberFormatException){ }
            }
        })

        annotation_zoom_cell = fragmentView.findViewById<LinearLayout>(R.id.annotation_zoom_cell)
        annotation_zoom_cell.findViewById<TextView>(R.id.settingTitle).text = resources.getString(R.string.annotation_show_title)
        annotation_zoom_cell.findViewById<TextView>(R.id.settingDetails).text = resources.getString(R.string.annotation_show_detail)
        annotation_zoom_cell.findViewById<TextView>(R.id.value_edit_text).text = getValueFromPreferences(DEFAULT_ANNOTATION_SHOW_VALUE,context!!).toString()
        annotation_zoom_cell.findViewById<TextView>(R.id.value_edit_text).addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(editable: Editable?) {}
            override fun beforeTextChanged(p0: CharSequence?, p1: Int, p2: Int, p3: Int) {}
            override fun onTextChanged(p0: CharSequence, p1: Int, p2: Int, p3: Int) {
                try { setValueToPreferences(DEFAULT_ANNOTATION_SHOW_VALUE,p0.toString().toFloat(),context!!) }
                catch (e: NumberFormatException){ }
            }
        })
    }


    override fun onCreateOptionsMenu(menu: Menu, inflater: MenuInflater) {
        inflater.inflate(R.menu.settings_menu, menu);
        super.onCreateOptionsMenu(menu, inflater)
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_restore_defaults ->{
                setValueToPreferences(DEFAULT_MAX_ZOOM_VALUE, DEFAULT_MAX_ZOOM_VALUE.first,context!!)
                setValueToPreferences(DEFAULT_ANNOTATION_SHOW_VALUE, DEFAULT_ANNOTATION_SHOW_VALUE.first,context!!)
                annotation_zoom_cell.findViewById<TextView>(R.id.value_edit_text).text = getValueFromPreferences(DEFAULT_ANNOTATION_SHOW_VALUE,context!!).toString()
                max_zoom_cell.findViewById<TextView>(R.id.value_edit_text).text = getValueFromPreferences(DEFAULT_MAX_ZOOM_VALUE,context!!).toString()
                return false
            }
            else -> return super.onOptionsItemSelected(item)
        }
    }

    override fun onClick(view: View) {
        when(view.id){
            R.id.add_button -> {
                val builder = AlertDialog.Builder(context!!)
                builder.setTitle(resources.getString(R.string.insert_flower_name));
                var input: EditText = EditText(activity);
                input.setInputType(InputType.TYPE_CLASS_TEXT);
                builder.setView(input);
                builder.setPositiveButton(
                    resources.getString(R.string.done_button)
                ) { dialog, which -> viewAdapter.insertItem(input.text.toString()) }
                builder.setNegativeButton(
                    resources.getString(R.string.cancel)
                ) { dialog, which -> dialog.cancel() }
                builder.show();
            }

            R.id.import_button -> {
                requestPermissions(arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE), READ_PHONE_STORAGE_RETURN_CODE)
            }
        }

    }

    override fun onAttach(context: Context) {
        super.onAttach(context)
        if (context is OnFragmentInteractionListener) {
            listener = context
        } else {
            throw RuntimeException(context.toString() + " must implement OnFragmentInteractionListener")
        }
    }

    override fun onDetach() {
        super.onDetach()
        listener = null
    }

    interface OnFragmentInteractionListener {
        // TODO: Update argument type and name
        fun onFragmentInteraction(uri: Uri)
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out kotlin.String>, grantResults: IntArray): Unit {
        if(requestCode == READ_PHONE_STORAGE_RETURN_CODE){
            if (permissions[0].equals(Manifest.permission.READ_EXTERNAL_STORAGE) && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = MimeTypeMap.getSingleton().getMimeTypeFromExtension("csv");
                }
                startActivityForResult(intent, READ_REQUEST_CODE)
            }
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, resultData: Intent?) {

        if (requestCode == READ_REQUEST_CODE && resultCode == AppCompatActivity.RESULT_OK) {
            resultData?.data?.also { uri ->
                readCSVFile(uri)
            }
        }
    }

    fun readCSVFile(uri: Uri){

        val resultList = mutableListOf<String>()
        val inputStream = context!!.getContentResolver().openInputStream(uri)
        val reader = BufferedReader(InputStreamReader(inputStream,"ISO-8859-1"))
        try {

            var csvLine: String? = reader.readLine()
            while (csvLine != null){
                val row = csvLine.split(",".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()
                resultList.addAll(row)
                csvLine = reader.readLine()
            }
        } catch (ex: IOException) {
            throw RuntimeException("Error in reading CSV file: $ex")
        } finally {
            try {
                inputStream.close()
            } catch (e: IOException) {
                throw RuntimeException("Error while closing input stream: $e")
            }
        }
        putFlowerListToPreferences(resultList,context!!)
        items = getFlowerListFromPreferences(context!!)
        viewAdapter.refresh(items)
    }

    override fun onHiddenChanged(hidden: Boolean) {
        super.onHiddenChanged(hidden)
        if(!hidden){
            items = getFlowerListFromPreferences(context!!)
            viewAdapter.refresh(items)
        }
    }


}
