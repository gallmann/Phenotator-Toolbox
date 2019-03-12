package com.masterthesis.johannes.annotationtool

import android.Manifest
import android.app.Activity
import android.content.Context
import android.net.Uri
import android.os.Bundle
import android.support.v4.app.Fragment
import android.view.*
import android.widget.*
import com.davemorrissey.labs.subscaleview.ImageSource
import android.content.pm.PackageManager
import android.os.Environment
import com.davemorrissey.labs.subscaleview.SubsamplingScaleImageView
import android.graphics.PointF
import android.widget.LinearLayout







class MainFragment : Fragment(), AdapterView.OnItemClickListener, View.OnClickListener {
    private var listener: OnFragmentInteractionListener? = null
    private lateinit var flowerListView: ListView
    private var annotationState: AnnotationState = AnnotationState()
    private lateinit var imageView: MyImageView
    private val READ_PHONE_STORAGE_RETURN_CODE: Int = 1
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setHasOptionsMenu(true)

    }


    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Inflate the layout for this fragment
        val fragmentView: View = inflater.inflate(R.layout.fragment_main, container, false)
        flowerListView = fragmentView.findViewById<ListView>(R.id.flower_list_view)
        flowerListView.onItemClickListener = this
        //updateFlowerListView()

        val imageViewContainer: LinearLayout = fragmentView.findViewById<LinearLayout>(R.id.imageViewContainer)

        imageView = MyImageView(context!!,annotationState,this)

        imageViewContainer.addView(imageView)

        requestPermissions(arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE), READ_PHONE_STORAGE_RETURN_CODE)

        /*
        var tileView: TileView = view.findViewById(R.id.imageView)
        TileView.Builder(tileView)
            .setSize(17934, 13452)
            .defineZoomLevel(0,"tiles/phi-1000000-%1\$d_%2\$d.jpg")
            .defineZoomLevel(1, "tiles/phi-500000-%1\$d_%2\$d.jpg")
            .defineZoomLevel(2, "tiles/phi-250000-%1\$d_%2\$d.jpg")
            .defineZoomLevel(3, "tiles/phi-125000-%1\$d_%2\$d.jpg")

            //.defineZoomLevel(1,"tiles/phi-500000-%1\$d_%2\$d.jpg")
            //.defineZoomLevel(2,"tiles/phi-250000-%1\$d_%2\$d.jpg")
            .build()

        //tileView.setScaleLimits(0F,30F)
        tileView.setMinimumScaleMode(ScalingScrollView.MinimumScaleMode.NONE)
*/
        return fragmentView

    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        updateFlowerListView()
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

    public fun updateFlowerListView(){
        if(annotationState.currentFlower == null){
            view!!.findViewById<LinearLayout>(R.id.annotation_edit_container).visibility = View.INVISIBLE
            flowerListView.adapter = null
        }
        else{
            view!!.findViewById<LinearLayout>(R.id.annotation_edit_container).visibility = View.VISIBLE
            var adapter = FlowerListAdapter(activity as Activity,annotationState)
            flowerListView.adapter = adapter
        }
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


    fun initImageView(){
        imageView.setImage(
            ImageSource.uri(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).toString() + "/tile_0_0.png").dimensions(
                22343,
                21929
            )
        );
        imageView.maxScale = 30.0F
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out kotlin.String>, grantResults: IntArray): Unit {
        if(requestCode == READ_PHONE_STORAGE_RETURN_CODE){
            if (permissions[0].equals(Manifest.permission.READ_EXTERNAL_STORAGE) && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                initImageView()
            }
        }
    }

    override fun onClick(imageView: View?) {


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
