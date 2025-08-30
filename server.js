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
const { Server } = require('socket.io'); // Use destructuring for clarity

const app = express();
const server = http.createServer(app);

// Configure CORS for Socket.IO. In a production environment, you should restrict the origin.
const io = new Server(server, {
    cors: {
        origin: "*", // Allow all origins for simplicity.
        methods: ["GET", "POST"]
    }
});

// In-memory store for users. For a production app, you'd use a database like Redis.
let users = {}; // Maps userId -> socket.id

io.on('connection', (socket) => {
    console.log(`A user connected: ${socket.id}`);

    // When a user logs in with their unique ID
    socket.on('login', (userId) => {
        if (!userId) return;
        console.log(`User logged in: ${userId} with socket ${socket.id}`);
        users[userId] = socket.id;
        socket.userId = userId; // Associate userId with the socket instance for easy lookup on disconnect

        // Broadcast the updated list of all online users to everyone
        io.emit('user-list', Object.keys(users));
        console.log('Current users:', users);
    });

    // Forwarding WebRTC offer to a target user
    socket.on('offer', (data) => {
        const { targetUserId, offer } = data;
        const targetSocketId = users[targetUserId];
        if (targetSocketId) {
            console.log(`Forwarding offer from ${socket.userId} to ${targetUserId}`);
            io.to(targetSocketId).emit('offer', { fromUserId: socket.userId, offer });
        } else {
            console.log(`Offer failed: Target user ${targetUserId} not found.`);
        }
    });

    // Forwarding WebRTC answer to a target user
    socket.on('answer', (data) => {
        const { targetUserId, answer } = data;
        const targetSocketId = users[targetUserId];
        if (targetSocketId) {
            console.log(`Forwarding answer from ${socket.userId} to ${targetUserId}`);
            io.to(targetSocketId).emit('answer', { fromUserId: socket.userId, answer });
        } else {
            console.log(`Answer failed: Target user ${targetUserId} not found.`);
        }
    });

    // Forwarding ICE candidates to a target user
    socket.on('ice-candidate', (data) => {
        const { targetUserId, candidate } = data;
        const targetSocketId = users[targetUserId];
        if (targetSocketId) {
            // This can be very noisy, so it's often commented out in production
            // console.log(`Forwarding ICE candidate from ${socket.userId} to ${targetUserId}`);
            io.to(targetSocketId).emit('ice-candidate', { fromUserId: socket.userId, candidate });
        }
    });

    // Handling and forwarding chat messages
    socket.on('chat-message', (data) => {
        const { targetUserId, message } = data;
        const targetSocketId = users[targetUserId];
        if (targetSocketId) {
            console.log(`Forwarding chat message from ${socket.userId} to ${targetUserId}`);
            // Send message to the target user
            io.to(targetSocketId).emit('chat-message', { fromUserId: socket.userId, message });
        }
    });

    // When a user disconnects
    socket.on('disconnect', () => {
        console.log(`User disconnected: ${socket.id}`);
        if (socket.userId) {
            console.log(`User ${socket.userId} logged out.`);
            delete users[socket.userId];
            // Broadcast the updated user list to everyone
            io.emit('user-list', Object.keys(users));
            console.log('Current users:', users);
        }
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));

