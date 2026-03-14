
async function send() {
            const input = document.getElementById('input');
            const text = input.value.trim();
            if(input.value === null || input.value === undefined || input.value === ''  || input.value.length === 0 || !text){
                alert("Please enter a valid message.");
                return;
            }
            
            
            if (text) {
                const messages = document.getElementById('messages');
                
            
                // Add user message (right side)
                const userMsg = document.createElement('div');
                userMsg.className = 'message user';
                userMsg.textContent = text;
                messages.appendChild(userMsg);
                
                
                
            sendData={
                text: input.value
            }   
            
            try{
                fetch('/chat', {
                method: 'POST',
                 headers: {
            'Content-Type': 'application/json'
                },
                body: JSON.stringify(sendData)  // Convert object to JSON string
            })
            .then(response => response.json())
            .then(data => {
            console.log('Flask replied:', data.statut);
            // Simulate sender reply after 0.5s
                setTimeout(() => {
                    const senderMsg = document.createElement('div');
                    senderMsg.className = 'message sender';
                    senderMsg.textContent = `✦: ${data.statut}`;
                    messages.appendChild(senderMsg);
                    messages.scrollTop = messages.scrollHeight;
                }, 500);
                });
            }    
            catch(error){
                console.error('Error:', error);
            };
            
            input.value = '';
            messages.scrollTop = messages.scrollHeight;
        }
    };
