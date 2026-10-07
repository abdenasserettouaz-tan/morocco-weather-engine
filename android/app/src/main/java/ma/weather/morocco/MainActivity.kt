package ma.weather.morocco

import android.annotation.SuppressLint
import android.app.Activity
import android.graphics.Bitmap
import android.os.Bundle
import android.view.View
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebResourceError
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import android.net.Uri
import android.content.Intent
import android.widget.ProgressBar
import android.widget.TextView

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private lateinit var progress: ProgressBar
    private lateinit var errorView: TextView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val root = android.widget.FrameLayout(this)
        webView = WebView(this)
        progress = ProgressBar(this)
        errorView = TextView(this).apply {
            text = "تعذر تحميل تطبيق الطقس. تحقق من الاتصال ثم اضغط لإعادة المحاولة."
            textSize = 17f
            gravity = android.view.Gravity.CENTER
            setPadding(40, 40, 40, 40)
            visibility = View.GONE
            setOnClickListener {
                visibility = View.GONE
                webView.reload()
            }
        }
        root.addView(webView, android.widget.FrameLayout.LayoutParams(-1, -1))
        root.addView(progress, android.widget.FrameLayout.LayoutParams(-2, -2, android.view.Gravity.CENTER))
        root.addView(errorView, android.widget.FrameLayout.LayoutParams(-1, -1))
        setContentView(root)

        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.allowFileAccess = false
        webView.settings.allowContentAccess = false
        webView.settings.setSupportZoom(false)
        webView.settings.builtInZoomControls = false
        webView.settings.mediaPlaybackRequiresUserGesture = true
        webView.settings.userAgentString = webView.settings.userAgentString + " MoroccoWeatherAndroid/1.0"

        val appOrigin = Uri.parse(BuildConfig.WEATHER_APP_URL)
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val uri = request?.url ?: return false
                val sameOrigin = uri.scheme == appOrigin.scheme && uri.host == appOrigin.host &&
                    effectivePort(uri) == effectivePort(appOrigin)
                if (sameOrigin) return false
                if (uri.scheme == "https" || uri.scheme == "http") {
                    startActivity(Intent(Intent.ACTION_VIEW, uri))
                    return true
                }
                return true
            }
            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                progress.visibility = View.VISIBLE
                errorView.visibility = View.GONE
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                progress.visibility = View.GONE
            }

            override fun onReceivedError(
                view: WebView?,
                request: WebResourceRequest?,
                error: WebResourceError?
            ) {
                if (request?.isForMainFrame == true) showLoadError()
            }

            override fun onReceivedHttpError(
                view: WebView?,
                request: WebResourceRequest?,
                errorResponse: WebResourceResponse?
            ) {
                if (request?.isForMainFrame == true && (errorResponse?.statusCode ?: 0) >= 400) {
                    showLoadError()
                }
            }
        }
        webView.webChromeClient = WebChromeClient()
        if (savedInstanceState == null) {
            webView.loadUrl(BuildConfig.WEATHER_APP_URL)
        } else {
            webView.restoreState(savedInstanceState)
        }
    }

    private fun effectivePort(uri: Uri): Int =
        if (uri.port != -1) uri.port else if (uri.scheme == "https") 443 else 80

    private fun showLoadError() {
        progress.visibility = View.GONE
        errorView.visibility = View.VISIBLE
    }

    override fun onSaveInstanceState(outState: Bundle) {
        webView.saveState(outState)
        super.onSaveInstanceState(outState)
    }

    override fun onResume() {
        super.onResume()
        webView.onResume()
    }

    override fun onPause() {
        webView.onPause()
        super.onPause()
    }

    override fun onDestroy() {
        webView.destroy()
        super.onDestroy()
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }
}
