package com.masterthesis.johannes.annotationtool

import android.net.Uri
import android.os.Bundle
import android.os.PersistableBundle
import android.provider.Settings
import com.google.android.material.navigation.NavigationView
import androidx.fragment.app.Fragment
import androidx.core.view.GravityCompat
import androidx.appcompat.app.ActionBarDrawerToggle
import androidx.appcompat.app.AppCompatActivity
import android.view.MenuItem
import kotlinx.android.synthetic.main.activity_main.*
import kotlinx.android.synthetic.main.app_bar_main.*



class MainActivity : AppCompatActivity(), NavigationView.OnNavigationItemSelectedListener,
    MainFragment.OnFragmentInteractionListener, SettingsFragment.OnFragmentInteractionListener {

    lateinit var currentFragment: Fragment
    var fragments: MutableMap<Int,Fragment> = mutableMapOf()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_main)

        if(savedInstanceState != null){
            loadFragment(savedInstanceState.getInt(CURRENT_FRAGMENT_KEY))
        }
        else{
            loadFragment(R.id.nav_annotations)
        }

        setSupportActionBar(toolbar)

        val toggle = ActionBarDrawerToggle(
            this, drawer_layout, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close
        )
        drawer_layout.addDrawerListener(toggle)
        toggle.syncState()

        nav_view.setNavigationItemSelectedListener(this)


    }

    override fun onBackPressed() {
        if (drawer_layout.isDrawerOpen(GravityCompat.START)) {
            drawer_layout.closeDrawer(GravityCompat.START)
        } else {
            super.onBackPressed()
        }
    }


    override fun onNavigationItemSelected(item: MenuItem): Boolean {
        // Handle navigation view item clicks here.
        loadFragment(item.itemId)
        drawer_layout.closeDrawer(GravityCompat.START)
        return true
    }



    fun loadFragment(id: Int){


        val transaction = supportFragmentManager.beginTransaction()
        if(::currentFragment.isInitialized){
            transaction.hide(currentFragment)
        }

        when (id) {
            R.id.nav_annotations -> {
                if(fragments.containsKey(id)){
                    currentFragment = fragments[id]!!
                }
                else{
                    currentFragment = MainFragment()
                    fragments[id] = currentFragment
                }
            }
            R.id.nav_settings -> {
                if(fragments.containsKey(id)){
                    currentFragment = fragments[id]!!
                }
                else{
                    currentFragment = SettingsFragment()
                    fragments[id] = currentFragment
                }
            }
        }
        if (currentFragment.isAdded()) { // if the fragment is already in container
            transaction.show(currentFragment);
        } else { // fragment needs to be added to frame container
            transaction.add(R.id.fragment_container, currentFragment, "A");
        }

        transaction.commit()
    }

    override fun onSaveInstanceState(outState: Bundle?) {
        // Save the user's current game state
        outState?.run {
            if(currentFragment is MainFragment) {
                putInt(CURRENT_FRAGMENT_KEY, R.id.nav_annotations)
            }
            else{
                putInt(CURRENT_FRAGMENT_KEY, R.id.nav_settings)
            }
        }

        // Always call the superclass so it can save the view hierarchy state
        super.onSaveInstanceState(outState)
    }



    public override fun onFragmentInteraction(uri: Uri): Unit {

    }
}
