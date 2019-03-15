package com.masterthesis.johannes.annotationtool

import android.content.Context
import android.net.Uri
import android.os.Bundle
import android.support.v4.app.Fragment
import android.view.*
import android.widget.AdapterView
import android.widget.ListView
import layout.SettingsListAdapter


class SettingsFragment : Fragment(), AdapterView.OnItemClickListener {

    private var listener: OnFragmentInteractionListener? = null
    private lateinit var settingsListView: ListView

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
        settingsListView = fragmentView.findViewById<ListView>(R.id.settingsListView)
        settingsListView.adapter = SettingsListAdapter(activity!!)


        return fragmentView
    }

    // TODO: Rename method, update argument and hook method into UI event
    fun onButtonPressed(uri: Uri) {
        listener?.onFragmentInteraction(uri)
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
                (settingsListView.adapter as SettingsListAdapter).notifyDataSetChanged()
                return false
            }
            else -> return super.onOptionsItemSelected(item)
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

    override fun onItemClick(p0: AdapterView<*>?, view: View?, index: Int, p3: Long) {
        println("bo")
    }

    interface OnFragmentInteractionListener {
        // TODO: Update argument type and name
        fun onFragmentInteraction(uri: Uri)
    }
}
