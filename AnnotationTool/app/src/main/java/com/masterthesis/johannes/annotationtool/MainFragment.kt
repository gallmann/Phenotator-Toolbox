package com.masterthesis.johannes.annotationtool

import android.app.Activity
import android.content.Context
import android.net.Uri
import android.os.Bundle
import android.support.v4.app.Fragment
import android.view.*
import android.support.v4.view.MenuItemCompat.getActionView
import android.widget.*


/**
 * A simple [Fragment] subclass.
 * Activities that contain this fragment must implement the
 * [MainFragment.OnFragmentInteractionListener] interface
 * to handle interaction events.
 * Use the [MainFragment.newInstance] factory method to
 * create an instance of this fragment.
 *
 */
class MainFragment : Fragment(), AdapterView.OnItemClickListener {
    private var listener: OnFragmentInteractionListener? = null
    private lateinit var flowerListView: ListView
    private var annotationState: AnnotationState = AnnotationState()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setHasOptionsMenu(true)

    }


    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Inflate the layout for this fragment
        val view: View = inflater.inflate(R.layout.fragment_main, container, false)
        flowerListView = view.findViewById<ListView>(R.id.flower_list_view)
        flowerListView.onItemClickListener = this
        updateFlowerListView()
        return view
    }


    override fun onCreateOptionsMenu(menu: Menu, inflater: MenuInflater) {
        inflater.inflate(R.menu.main, menu);
        super.onCreateOptionsMenu(menu, inflater)

        enableMenuItem(menu.findItem(R.id.action_redo), false)
        enableMenuItem(menu.findItem(R.id.action_undo), false)
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        when (item.itemId) {
            else -> return super.onOptionsItemSelected(item)
        }
    }

    override fun onItemClick(p0: AdapterView<*>?, view: View, index: Int, p3: Long) {

        (flowerListView.adapter as FlowerListAdapter).selectedIndex(index)
    }


    fun enableMenuItem(button: MenuItem, enable: Boolean){
        if(enable){
            button.icon.alpha = 0
            button.setEnabled(true)
        }
        else {
            button.icon.alpha = 120
            button.setEnabled(false)
        }
    }

    fun updateFlowerListView(){
        var listItems: Array<String> = arrayOf("Sonnenblume", "Löwenzahn", "bla", "bla", "b", "hhh", "hf", "fhewf")
        val adapter = FlowerListAdapter(activity as Activity , annotationState)
        flowerListView.adapter = adapter
    }

    // TODO: Rename method, update argument and hook method into UI event
    fun onButtonPressed(uri: Uri) {
        listener?.onFragmentInteraction(uri)
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

    /**
     * This interface must be implemented by activities that contain this
     * fragment to allow an interaction in this fragment to be communicated
     * to the activity and potentially other fragments contained in that
     * activity.
     *
     *
     * See the Android Training lesson [Communicating with Other Fragments]
     * (http://developer.android.com/training/basics/fragments/communicating.html)
     * for more information.
     */
    interface OnFragmentInteractionListener {
        // TODO: Update argument type and name
        fun onFragmentInteraction(uri: Uri)
    }




}
