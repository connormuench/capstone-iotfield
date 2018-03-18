App.users = App.cable.subscriptions.create({channel: "UserNotificationsChannel"}, {
    connected: function() {
        console.log("connected");
        // Called when the subscription is ready for use on the server
    },
    disconnected: function() {
        console.log("disconnected");
    }, 
    received: function(data) {
        // Called when there's incoming data on the websocket for this channel
    }
});
