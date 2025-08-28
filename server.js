/**
 * Signaling Server for the Network Dating WebRTC Application.
 *
 * This server does not store any user data or handle any game logic.
 * Its sole purpose is to act as a "matchmaker" or "switchboard" to introduce
 * two clients to each other so they can form a direct peer-to-peer (P2P) connection.
 * This process is called "signaling".
 *
 * It listens for specific messages from clients and forwards them to the intended recipient.
 */

const http = require('http');
const socketIo = require('socket.io');

const server = http.createServer();
const io = socketIo(server, {
    cors: {
        origin: "*", // In production, restrict this to your frontend's domain for security.
    }
});

// Handle incoming connections from clients.
io.on('connection', (socket) => {
    console.log('A user connected:', socket.id);

    // --- WebRTC Signaling ---
    // Forward the WebRTC signaling data (offers, answers, candidates) to the correct peer.
    socket.on('signal', (data) => {
        const { to, from, signal } = data;
        console.log(`Forwarding signal from ${from} to ${to}`);
        socket.to(to).emit('signal', { from, signal });
    });

    // --- User Discovery ---
    // When a new user joins, inform all other connected users.
    // The new user will then initiate a connection with each of them.
    socket.broadcast.emit('user-joined', { userId: socket.id });

    // When a user disconnects, inform all other users so they can clean up the connection.
    socket.on('disconnect', () => {
        console.log('User disconnected:', socket.id);
        io.emit('user-left', { userId: socket.id });
    });
});

// Start the server. Render.com will automatically use the PORT environment variable.
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Signaling server running on port ${PORT}`);
    console.log('Ready to broker connections!');
});