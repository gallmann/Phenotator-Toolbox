package com.masterthesis.johannes.annotationtool

import android.Manifest
import androidx.appcompat.app.AppCompatActivity
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.*
import android.widget.*
import android.content.pm.PackageManager
import android.widget.LinearLayout
import android.content.Context.MODE_PRIVATE
import android.content.IntentSender
import com.google.android.material.snackbar.Snackbar
import androidx.core.content.ContextCompat
import com.google.android.gms.common.api.ResolvableApiException
import com.google.android.gms.location.*
import com.google.android.gms.tasks.Task
import java.io.File
import com.davemorrissey.labs.subscaleview.ImageViewState
import android.R.id
import com.davemorrissey.labs.subscaleview.SubsamplingScaleImageView




class MainFragment : Fragment(), AdapterView.OnItemClickListener, View.OnClickListener {
    private var listener: OnFragmentInteractionListener? = null
    private lateinit var flowerListView: ListView
    private lateinit var annotationState: AnnotationState
    private lateinit var imageView: MyImageView
    private val READ_PHONE_STORAGE_RETURN_CODE: Int = 1
    private val READ_PHONE_STORAGE_RETURN_CODE_STARTUP: Int = 2
    var restoredImageViewState: ImageViewState? = null

    private lateinit var fusedLocationClient: FusedLocationProviderClient
    private lateinit var locationCallback: LocationCallback

    private lateinit var imagePath: String
    val OPEN_IMAGE_REQUEST_CODE: Int = 42



    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setHasOptionsMenu(true)
        fusedLocationClient = LocationServices.getFusedLocationProviderClient(activity!!)
        locationCallback = object : LocationCallback() {
            override fun onLocationResult(locationResult: LocationResult?) {
                locationResult ?: return
                for (location in locationResult.locations){
                    imageView.updateLocation(location)
                }
            }
        }

    }


    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Inflate the layout for this fragment
        val fragmentView: View = inflater.inflate(R.layout.fragment_main, container, false)
        flowerListView = fragmentView.findViewById<ListView>(R.id.flower_list_view)
        flowerListView.onItemClickListener = this
        fragmentView.findViewById<LinearLayout>(R.id.annotation_edit_container).visibility = View.INVISIBLE

        fragmentView.findViewById<Button>(R.id.done_button).setOnClickListener(this)
        fragmentView.findViewById<Button>(R.id.cancel_button).setOnClickListener(this)
        fragmentView.findViewById<ImageButton>(R.id.upButton).setOnClickListener(this)
        fragmentView.findViewById<ImageButton>(R.id.downButton).setOnClickListener(this)
        fragmentView.findViewById<ImageButton>(R.id.leftButton).setOnClickListener(this)
        fragmentView.findViewById<ImageButton>(R.id.rightButton).setOnClickListener(this)

        return fragmentView
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        if(savedInstanceState != null && savedInstanceState.containsKey(IMAGE_VIEW_STATE_KEY)) {
            restoredImageViewState = savedInstanceState.getSerializable(IMAGE_VIEW_STATE_KEY) as ImageViewState
        }

        val prefs = context!!.getSharedPreferences(SHARED_PREFERENCES_KEY, MODE_PRIVATE)
        val restoredText = prefs.getString(LAST_OPENED_IMAGE_URI, null)
        if (restoredText != null) {
            imagePath = restoredText
            requestPermissions(arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE), READ_PHONE_STORAGE_RETURN_CODE_STARTUP)
        }


    }


    override fun onCreateOptionsMenu(menu: Menu, inflater: MenuInflater) {
        inflater.inflate(R.menu.main, menu);
        super.onCreateOptionsMenu(menu, inflater)
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        when (item.itemId) {
            R.id.action_import_image ->{
                openImage()
                return false
            }
            else -> return super.onOptionsItemSelected(item)
        }
    }

    override fun onItemClick(p0: AdapterView<*>?, view: View, index: Int, p3: Long) {

        (flowerListView.adapter as FlowerListAdapter).selectedIndex(index)
        imageView.invalidate()
    }


    public fun updateFlowerListView(){
        if(annotationState.currentFlower == null){
            view!!.findViewById<LinearLayout>(R.id.annotation_edit_container).visibility = View.INVISIBLE
            flowerListView.adapter = null
        }
        else{
            view!!.findViewById<LinearLayout>(R.id.annotation_edit_container).visibility = View.VISIBLE
            var adapter = FlowerListAdapter(activity as AppCompatActivity,annotationState)
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


        if(!isExternalStorageWritable() || !File(imagePath).exists()){
            Snackbar.make(view!!, R.string.could_not_load_image, Snackbar.LENGTH_LONG).show();
            val editor = context!!.getSharedPreferences(SHARED_PREFERENCES_KEY, MODE_PRIVATE).edit()
            editor.putString(LAST_OPENED_IMAGE_URI,null)
            editor.apply()
            return
        }
        println(imagePath)
        view!!.findViewById<ProgressBar>(R.id.progress_circular).visibility = View.VISIBLE
        view!!.findViewById<ProgressBar>(R.id.progress_circular).bringToFront()
        annotationState = AnnotationState(imagePath,context!!)
        val imageViewContainer: RelativeLayout = view!!.findViewById<RelativeLayout>(R.id.imageViewContainer)



        if(::imageView.isInitialized){
            imageView.reload(annotationState,this)
            //imageViewContainer.removeView(imageView)
        }
        else{
            imageView = MyImageView(context!!,annotationState,this, stateToRestore = restoredImageViewState)
            imageViewContainer.addView(imageView)
        }


        val editor = context!!.getSharedPreferences(SHARED_PREFERENCES_KEY, MODE_PRIVATE).edit()
        editor.putString(LAST_OPENED_IMAGE_URI,imagePath)
        editor.apply()
        if(annotationState.hasLocationInformation()){
            startLocationUpdates()
        }
    }

    private fun stopLocationUpdates() {
        fusedLocationClient.removeLocationUpdates(locationCallback)
    }

    private fun startLocationUpdates(){
        if (ContextCompat.checkSelfPermission(activity!!, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION), LOCATION_PERMISSION_REQUEST)
        }
        else{
            val locationRequest = LocationRequest.create()?.apply {
                interval = 6000
                fastestInterval = 3000
                priority = LocationRequest.PRIORITY_HIGH_ACCURACY
            }
            val builder = LocationSettingsRequest.Builder()
                .addLocationRequest(locationRequest!!)
            val client: SettingsClient = LocationServices.getSettingsClient(activity!!)
            val task: Task<LocationSettingsResponse> = client.checkLocationSettings(builder.build())
            task.addOnSuccessListener { locationSettingsResponse ->
                fusedLocationClient.requestLocationUpdates(locationRequest,
                    locationCallback,
                    null /* Looper */)
            }

            task.addOnFailureListener { exception ->
                if (exception is ResolvableApiException){
                    try {
                        startIntentSenderForResult(exception.getResolution().getIntentSender(), TURN_ON_LOCATION_USER_REQUEST, null, 0, 0, 0, null);
                    } catch (sendEx: IntentSender.SendIntentException) {
                    }
                }
            }



        }
    }


    override fun onClick(view: View) {
        when(view.id){
            R.id.done_button -> {
                annotationState.permanentlyAddCurrentFlower()
                updateFlowerListView()
                imageView.invalidate()
            }
            R.id.cancel_button -> {
                annotationState.cancelCurrentFlower()
                updateFlowerListView()
                imageView.invalidate()
            }
            R.id.upButton, R.id.downButton, R.id.leftButton, R.id.rightButton -> {
                moveCurrentMark(view.id)
            }
        }
    }

    private fun moveCurrentMark(id: Int){
        when(id){
            R.id.leftButton -> {
                annotationState.currentFlower!!.xPos = annotationState.currentFlower!!.xPos - 1
            }
            R.id.rightButton -> {
                annotationState.currentFlower!!.xPos = annotationState.currentFlower!!.xPos + 1
            }
            R.id.upButton -> {
                annotationState.currentFlower!!.yPos = annotationState.currentFlower!!.yPos - 1
            }
            R.id.downButton -> {
                annotationState.currentFlower!!.yPos = annotationState.currentFlower!!.yPos + 1
            }
        }
        imageView.invalidate()
    }


    private fun openImage(){
        requestPermissions(arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE), READ_PHONE_STORAGE_RETURN_CODE)
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out kotlin.String>, grantResults: IntArray): Unit {
        if(requestCode == READ_PHONE_STORAGE_RETURN_CODE){
            if (permissions[0].equals(Manifest.permission.READ_EXTERNAL_STORAGE) && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "image/*"
                }
                startActivityForResult(intent, OPEN_IMAGE_REQUEST_CODE)
            }
        }
        else if(requestCode == READ_PHONE_STORAGE_RETURN_CODE_STARTUP){
            if (grantResults.isNotEmpty() && permissions[0].equals(Manifest.permission.READ_EXTERNAL_STORAGE) && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                initImageView()
            }

        }
        else if(requestCode == LOCATION_PERMISSION_REQUEST) {
            //TODO: arrayoutofbounds exception
            if (grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                startLocationUpdates()
            }
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, resultData: Intent?) {

        if (requestCode == OPEN_IMAGE_REQUEST_CODE && resultCode == AppCompatActivity.RESULT_OK) {
            resultData?.data?.also { uri ->
                imagePath = uriToPath(uri)
                initImageView()
            }
        }
        if (requestCode == TURN_ON_LOCATION_USER_REQUEST) {
            startLocationUpdates()
        }
    }

    override fun onResume() {
        super.onResume()
        if(::annotationState.isInitialized){
            if (annotationState.hasLocationInformation()){
                stopLocationUpdates()
                startLocationUpdates()
            }
        }
    }

    override fun onPause() {
        super.onPause()
        stopLocationUpdates()
    }


    override fun onSaveInstanceState(outState: Bundle) {
        val state = imageView.state
        if (state != null) {
            outState.putSerializable(IMAGE_VIEW_STATE_KEY, imageView.state)
        }
        imageView.recycle()
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
