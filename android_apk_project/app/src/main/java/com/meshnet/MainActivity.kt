package com.meshnet

import android.os.Bundle
import android.webkit.WebSettings
import android.webkit.WebView
import androidx.appcompat.app.AppCompatActivity

/**
 * MeshNet Android client shell (launch-ready scaffold).
 * Protocol alignment: signed invites (QR/NFC/BLE/manual), one UDP socket per node on OS-assigned port,
 * compression-encrypted authenticated envelopes, replay protection, hail on connect, '?' complete objective/help,
 * routes/ping/chat/groups, Blockchain of messages, Sensei Network Map UI.
 * Extend with native UDP foreground service + QR/NFC/BLE bootstrap + local key storage.
 */
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val webView = WebView(this)
        val settings: WebSettings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        setContentView(webView)
        // Bundled MeshNet UI (assets/meshnet.html). Set ?api=http://<session-host>:<port> for live session.
        webView.loadUrl("file:///android_asset/meshnet.html")
    }
}
