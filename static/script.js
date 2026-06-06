document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-btn');
    const topicInput = document.getElementById('topic');
    const roundsInput = document.getElementById('rounds');
    const loader = document.getElementById('loader');
    const container = document.getElementById('debate-container');
    const errorMsg = document.getElementById('error-msg');

    startBtn.addEventListener('click', async () => {
        const topic = topicInput.value.trim();
        const rounds = parseInt(roundsInput.value);

        if (!topic) {
            showError("Please enter a debate topic.");
            return;
        }
        if (isNaN(rounds) || rounds < 1 || rounds > 5) {
            showError("Please enter a valid number of rounds (1-5).");
            return;
        }

        // Reset UI
        errorMsg.style.display = 'none';
        container.innerHTML = '';
        startBtn.disabled = true;
        loader.style.display = 'block';

        try {
            const response = await fetch('/debate/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ topic, rounds })
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => null);
                throw new Error(errData?.detail || `HTTP Error: ${response.status}`);
            }

            const data = await response.json();
            loader.style.display = 'none'; // Hide spinner before animation starts
            await renderMessages(data.messages);

        } catch (error) {
            showError(`Simulation failed: ${error.message}`);
        } finally {
            startBtn.disabled = false;
            loader.style.display = 'none';
        }
    });

    function showError(message) {
        errorMsg.textContent = message;
        errorMsg.style.display = 'block';
    }

    async function renderMessages(messages) {
        if (!messages || messages.length === 0) {
            container.innerHTML = '<p class="subtitle" style="text-align:center;">No debate generated.</p>';
            return;
        }

        const flags = {
            'USA': '🇺🇸',
            'EU': '🇪🇺',
            'China': '🇨🇳'
        };

        for (const msg of messages) {
            const card = document.createElement('div');
            const agentClass = msg.agent ? `agent-${msg.agent.toLowerCase()}` : '';
            const stanceClass = msg.stance ? `stance-${msg.stance.toLowerCase()}` : '';
            const flag = flags[msg.agent] || '';

            // Format timestamp
            const date = new Date(msg.timestamp);
            const timeString = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            card.className = `message-card ${agentClass}`;

            card.innerHTML = `
                <div class="message-header">
                    <span class="agent-name">${flag} ${msg.agent}</span>
                    <span class="stance-badge ${stanceClass}">${msg.stance}</span>
                </div>
                <div class="message-content">
                    ${msg.message.replace(/\n/g, '<br>')}
                </div>
                <div class="meta-info">
                    <span>Round ${msg.round}</span>
                    <span>${timeString}</span>
                </div>
            `;

            container.appendChild(card);

            // Auto-scroll to the bottom so the user tracks the conversation
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

            // Wait 1.5 seconds before injecting the next message
            await new Promise(r => setTimeout(r, 1500));
        }
    }
});
