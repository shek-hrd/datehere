/**
 * Signaling and Web Server for the DateHereNow WebRTC Application.
 *
 * This server has two main responsibilities:
 * 1.  **Signaling Server (using Socket.IO)**: It acts as a "matchmaker" or "switchboard" 
 *     to introduce two clients to each other so they can form a direct peer-to-peer (P2P) 
 *     connection. This process is called "signaling". It doesn't handle any video/audio data.
 * 2.  **Web Server (using Express)**: It serves the main application files (HTML, CSS, JS)
 *     to the users' browsers.
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);

// Configure Socket.IO with CORS settings
// In production, you should restrict the origin to your frontend's domain for security.
const io = socketIo(server, {
    cors: {
        origin: "*", 
    }
});

// --- Web Server Logic ---
// Serve the static files for the client-side application (index.html, style.css, app.js)
const publicPath = path.join(__dirname, 'public');
app.use(express.static(publicPath));

log('Server is configured to serve static files from: ' + publicPath);

// --- Signaling Server Logic ---
io.on('connection', (socket) => {
    log(`User connected with ID: ${socket.id}`);

    // --- User Discovery ---
    // When a new user connects, send them a list of all other connected users.
    const otherUsers = Array.from(io.sockets.sockets.keys()).filter(id => id !== socket.id);
    socket.emit('users-present', otherUsers);
    log(`Sent 'users-present' to ${socket.id} with users: [${otherUsers.join(', ')}]`);

    // Announce the new user to everyone else so they can add them to their list.
    socket.broadcast.emit('user-joined', socket.id);
    log(`Broadcast 'user-joined' for new user: ${socket.id}`);

    // --- WebRTC Signaling ---
    // Forward signaling data (offers, answers, candidates) to the correct peer.
    socket.on('signal', (data) => {
        const { to, from, signal } = data;
        console.log(`Forwarding signal from ${from} to ${to}`);
        // Emit the signal directly to the intended recipient's socket.
        io.to(to).emit('signal', { from, signal });
    });

    // --- Disconnection ---
    // When a user disconnects, inform all other users so they can clean up the connection.
    socket.on('disconnect', () => {
        log(`User disconnected: ${socket.id}`);
        // The client-side app.js expects the raw socket ID.
        io.emit('user-left', socket.id);
    });
});

/**
 * Simple server-side logger.
 * @param {string} message - The message to log.
 */
function log(message) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${message}`);
}

// Start the server. Render.com or other services will use the PORT environment variable.
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    log(`Signaling server running on http://localhost:${PORT}`);
    log('Ready to broker connections and serve the app!');
});