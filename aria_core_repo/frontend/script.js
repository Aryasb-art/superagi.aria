// AriaRobot Frontend JavaScript
class AriaRobotClient {
    constructor() {
        // Use relative URL when served from the same server
        this.apiBase = window.location.origin;
        this.init();
    }

    init() {
        // Initialize UI components
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.responseSection = document.getElementById('responseSection');
        this.responseContent = document.getElementById('responseContent');
        this.loadingSection = document.getElementById('loadingSection');
        this.memorySection = document.getElementById('memorySection');
        this.memoryContent = document.getElementById('memoryContent');
        
        // Status elements
        this.agentStatus = document.getElementById('agentStatus');
        this.memoryStatus = document.getElementById('memoryStatus');
        this.connectionStatus = document.getElementById('connectionStatus');
        
        // Sentiment analysis elements
        this.sentimentInput = document.getElementById('sentimentInput');
        this.sentimentBtn = document.getElementById('sentimentBtn');
        this.sentimentResult = document.getElementById('sentimentResult');
        this.sentimentContent = document.getElementById('sentimentContent');
        this.sentimentLoading = document.getElementById('sentimentLoading');
        
        // Text summarization elements
        this.summaryInput = document.getElementById('summaryInput');
        this.summaryBtn = document.getElementById('summaryBtn');
        this.summaryResult = document.getElementById('summaryResult');
        this.summaryContent = document.getElementById('summaryContent');
        this.summaryLoading = document.getElementById('summaryLoading');
        
        // Long-term memory elements
        this.memoryInput = document.getElementById('memoryInput');
        this.memoryCategory = document.getElementById('memoryCategory');
        this.memoryTags = document.getElementById('memoryTags');
        this.saveMemoryBtn = document.getElementById('saveMemoryBtn');
        this.fetchMemoriesBtn = document.getElementById('fetchMemoriesBtn');
        this.memoryResult = document.getElementById('memoryResult');
        this.memoryContent = document.getElementById('memoryContent');
        this.memoryLoading = document.getElementById('memoryLoading');
        
        // Conceptual memory elements
        this.conceptualInput = document.getElementById('conceptualInput');
        this.analyzeConceptBtn = document.getElementById('analyzeConceptBtn');
        this.fetchConceptsBtn = document.getElementById('fetchConceptsBtn');
        this.conceptualResult = document.getElementById('conceptualResult');
        this.conceptualContent = document.getElementById('conceptualContent');
        this.conceptualLoading = document.getElementById('conceptualLoading');
        
        // Repetitive learning elements
        this.repetitiveInput = document.getElementById('repetitiveInput');
        this.observePatternBtn = document.getElementById('observePatternBtn');
        this.fetchPatternsBtn = document.getElementById('fetchPatternsBtn');
        this.repetitiveResult = document.getElementById('repetitiveResult');
        this.repetitiveContent = document.getElementById('repetitiveContent');
        this.repetitiveLoading = document.getElementById('repetitiveLoading');
        
        // Knowledge graph elements
        this.knowledgeGraphInput = document.getElementById('knowledgeGraphInput');
        this.buildGraphBtn = document.getElementById('buildGraphBtn');
        this.listGraphsBtn = document.getElementById('listGraphsBtn');
        this.knowledgeGraphResult = document.getElementById('knowledgeGraphResult');
        this.knowledgeGraphContent = document.getElementById('knowledgeGraphContent');
        this.knowledgeGraphLoading = document.getElementById('knowledgeGraphLoading');
        
        // Auto suggester elements
        this.suggesterInput = document.getElementById('suggesterInput');
        this.getCompletionBtn = document.getElementById('getCompletionBtn');
        this.getHintsBtn = document.getElementById('getHintsBtn');
        this.getSmartSuggestionsBtn = document.getElementById('getSmartSuggestionsBtn');
        this.suggesterResult = document.getElementById('suggesterResult');
        this.suggesterContent = document.getElementById('suggesterContent');
        this.suggesterLoading = document.getElementById('suggesterLoading');
        
        // Goal inference elements
        this.goalInferenceInput = document.getElementById('goalInferenceInput');
        this.analyzeGoalBtn = document.getElementById('analyzeGoalBtn');
        this.clearGoalAnalysisBtn = document.getElementById('clearGoalAnalysisBtn');
        this.goalInferenceResult = document.getElementById('goalInferenceResult');
        this.goalInferenceContent = document.getElementById('goalInferenceContent');
        this.goalInferenceLoading = document.getElementById('goalInferenceLoading');
        
        // Emotion regulation elements
        this.emotionInput = document.getElementById('emotionInput');
        this.analyzeEmotionBtn = document.getElementById('analyzeEmotionBtn');
        this.clearEmotionAnalysisBtn = document.getElementById('clearEmotionAnalysisBtn');
        this.emotionResult = document.getElementById('emotionResult');
        this.emotionContent = document.getElementById('emotionContent');
        this.emotionLoading = document.getElementById('emotionLoading');
        
        // Decision support elements
        this.decisionInput = document.getElementById('decisionInput');
        this.analyzeDecisionBtn = document.getElementById('analyzeDecisionBtn');
        this.clearDecisionAnalysisBtn = document.getElementById('clearDecisionAnalysisBtn');
        this.listDecisionsBtn = document.getElementById('listDecisionsBtn');
        this.decisionResult = document.getElementById('decisionResult');
        this.decisionContent = document.getElementById('decisionContent');
        this.decisionLoading = document.getElementById('decisionLoading');
        
        // Reward elements
        this.rewardInput = document.getElementById('rewardInput');
        this.analyzeRewardBtn = document.getElementById('analyzeRewardBtn');
        this.rewardResult = document.getElementById('rewardResult');
        this.rewardContent = document.getElementById('rewardContent');
        this.rewardLoading = document.getElementById('rewardLoading');
        
        // Bias detection elements
        this.biasInput = document.getElementById('biasInput');
        this.analyzeBiasBtn = document.getElementById('analyzeBiasBtn');
        this.biasResult = document.getElementById('biasResult');
        this.biasContent = document.getElementById('biasContent');
        this.biasLoading = document.getElementById('biasLoading');
        
        // Cognitive distortion elements
        this.distortionInput = document.getElementById('distortionInput');
        this.analyzeDistortionBtn = document.getElementById('analyzeDistortionBtn');
        this.distortionResult = document.getElementById('distortionResult');
        this.distortionContent = document.getElementById('distortionContent');
        this.distortionLoading = document.getElementById('distortionLoading');
        
        // Ethical reasoning elements
        this.ethicalInput = document.getElementById('ethicalInput');
        this.analyzeEthicalBtn = document.getElementById('analyzeEthicalBtn');
        this.ethicalResult = document.getElementById('ethicalResult');
        this.ethicalContent = document.getElementById('ethicalContent');
        this.ethicalLoading = document.getElementById('ethicalLoading');

        // Check initial system status
        this.checkSystemStatus();
        
        // Auto-refresh status every 30 seconds
        setInterval(() => this.checkSystemStatus(), 30000);
    }

    // Send message to Agent
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) {
            this.showNotification('لطفاً پیامی وارد کنید.', 'warning');
            return;
        }

        this.showLoading(true);
        this.sendBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/agent/public`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.displayResponse(data);
            this.messageInput.value = '';

        } catch (error) {
            console.error('Error sending message:', error);
            this.showNotification('خطا در ارسال پیام. لطفاً دوباره تلاش کنید.', 'error');
            this.connectionStatus.textContent = 'خطا در اتصال';
            this.connectionStatus.className = 'text-red-600';
        } finally {
            this.showLoading(false);
            this.sendBtn.disabled = false;
        }
    }

    // Display Agent response
    displayResponse(data) {
        if (data.success) {
            this.responseContent.innerHTML = `
                <div class="chat-message">
                    <div class="flex items-start gap-3">
                        <div class="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <div class="flex-1">
                            <div class="bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                                <p class="text-gray-800 leading-relaxed">${data.content}</p>
                            </div>
                            <div class="text-xs text-gray-500 mt-1">
                                <span>پاسخ از: ${data.handled_by}</span>
                                <span class="mr-4">زمان: ${this.formatTime(data.timestamp)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            this.responseSection.classList.remove('hidden');
            this.showNotification('پاسخ دریافت شد', 'success');
        } else {
            this.responseContent.innerHTML = `
                <div class="chat-message">
                    <div class="bg-red-50 border border-red-200 p-3 rounded-lg">
                        <p class="text-red-800">خطا: ${data.content}</p>
                        ${data.error ? `<p class="text-red-600 text-sm mt-1">جزئیات: ${data.error}</p>` : ''}
                    </div>
                </div>
            `;
            this.responseSection.classList.remove('hidden');
            this.showNotification('خطا در پردازش پیام', 'error');
        }
    }

    // Show Agent memory
    async showMemory() {
        try {
            const response = await fetch(`${this.apiBase}/agent/memory`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ message: 'show memory' })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.displayMemory(data.content);
            this.memorySection.classList.remove('hidden');
            this.showNotification('حافظه نمایش داده شد', 'success');

        } catch (error) {
            console.error('Error fetching memory:', error);
            this.showNotification('خطا در نمایش حافظه', 'error');
        }
    }

    // Clear Agent memory
    async clearMemory() {
        if (!confirm('آیا مطمئن هستید که می‌خواهید حافظه را پاک کنید؟')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/agent/memory`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ message: 'clear memory' })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.showNotification('حافظه پاک شد', 'success');
            this.memorySection.classList.add('hidden');
            this.memoryStatus.textContent = 'پاک شده';

        } catch (error) {
            console.error('Error clearing memory:', error);
            this.showNotification('خطا در پاک کردن حافظه', 'error');
        }
    }

    // Display memory content
    displayMemory(content) {
        if (content.includes('حافظه خالی است')) {
            this.memoryContent.innerHTML = `
                <div class="text-center text-gray-500 py-8">
                    <svg class="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    <p>حافظه خالی است</p>
                </div>
            `;
        } else {
            // Parse memory content
            const lines = content.split('\n');
            const memoryLines = lines.filter(line => line.startsWith('- '));
            const statusLine = lines.find(line => line.includes('وضعیت حافظه'));

            let html = '<div class="space-y-2">';
            
            if (memoryLines.length > 0) {
                html += '<h4 class="font-medium text-gray-700 mb-2">آخرین پیام‌ها:</h4>';
                memoryLines.forEach(line => {
                    const cleanLine = line.replace('- ', '');
                    const isUser = cleanLine.startsWith('User:');
                    const isAgent = cleanLine.startsWith('Agent:');
                    
                    html += `
                        <div class="flex items-start gap-2 p-2 rounded ${isUser ? 'bg-blue-50' : isAgent ? 'bg-green-50' : 'bg-gray-50'}">
                            <div class="w-2 h-2 rounded-full mt-2 ${isUser ? 'bg-blue-500' : isAgent ? 'bg-green-500' : 'bg-gray-500'}"></div>
                            <span class="text-sm">${cleanLine}</span>
                        </div>
                    `;
                });
            }

            if (statusLine) {
                html += `<div class="mt-4 p-2 bg-gray-100 rounded text-sm text-gray-600">${statusLine}</div>`;
                
                // Update memory status
                const match = statusLine.match(/(\d+)\/(\d+)/);
                if (match) {
                    this.memoryStatus.textContent = `${match[1]}/${match[2]} پیام`;
                }
            }

            html += '</div>';
            this.memoryContent.innerHTML = html;
        }
    }

    // Check system status
    async checkSystemStatus() {
        try {
            // Check API health
            const healthResponse = await fetch(`${this.apiBase}/health`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                mode: 'cors'
            });
            
            if (healthResponse.ok) {
                const healthData = await healthResponse.json();
                this.connectionStatus.textContent = 'متصل';
                this.connectionStatus.className = 'text-green-600';
                this.agentStatus.textContent = 'فعال';
                this.agentStatus.className = 'text-green-600';
                
                // Test agent response
                const agentTest = await fetch(`${this.apiBase}/agent/public`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                    },
                    mode: 'cors',
                    body: JSON.stringify({ message: 'status check' })
                });
                
                if (agentTest.ok) {
                    const agentData = await agentTest.json();
                    if (agentData.success) {
                        this.agentStatus.textContent = 'فعال';
                        this.agentStatus.className = 'text-green-600';
                    }
                }
            } else {
                throw new Error(`Health check failed: ${healthResponse.status}`);
            }

        } catch (error) {
            console.error('System status check failed:', error);
            this.connectionStatus.textContent = 'قطع شده';
            this.connectionStatus.className = 'text-red-600';
            this.agentStatus.textContent = 'غیرفعال';
            this.agentStatus.className = 'text-red-600';
        }
    }

    // Utility functions
    showLoading(show) {
        if (show) {
            this.loadingSection.classList.remove('hidden');
            this.responseSection.classList.add('hidden');
        } else {
            this.loadingSection.classList.add('hidden');
        }
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('fa-IR', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 left-4 z-50 px-4 py-2 rounded-lg shadow-lg transition-all duration-300 ${
            type === 'success' ? 'bg-green-500 text-white' :
            type === 'error' ? 'bg-red-500 text-white' :
            type === 'warning' ? 'bg-yellow-500 text-white' :
            'bg-blue-500 text-white'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // Analyze sentiment
    async analyzeSentiment() {
        const text = this.sentimentInput.value.trim();
        if (!text) {
            this.showNotification('لطفاً متنی برای تحلیل وارد کنید.', 'warning');
            return;
        }

        this.showSentimentLoading(true);
        this.sentimentBtn.disabled = true;

        try {
            // Prepare message for ToolAgent
            const message = `تحلیل احساس: ${text}`;
            
            const response = await fetch(`${this.apiBase}/agent/tool/public`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displaySentimentResult(data.content, text);
            } else {
                throw new Error(data.error || 'خطا در تحلیل احساسات');
            }

        } catch (error) {
            console.error('Sentiment analysis error:', error);
            this.showNotification(`خطا در تحلیل احساسات: ${error.message}`, 'error');
        } finally {
            this.showSentimentLoading(false);
            this.sentimentBtn.disabled = false;
        }
    }

    // Display sentiment analysis result
    displaySentimentResult(content, originalText) {
        // Parse the content to extract sentiment info
        const lines = content.split('\n');
        let sentiment = 'خنثی';
        let emoji = '😐';
        let polarity = '0.000';
        let subjectivity = '0.000';
        
        // Extract sentiment from response
        const sentimentMatch = content.match(/\*\*نتیجه:\*\* (.+)/);
        if (sentimentMatch) {
            sentiment = sentimentMatch[1].trim();
        }
        
        // Extract emoji
        const emojiMatch = content.match(/([😊😞😐🤔]) \*\*نتیجه:\*\*/);
        if (emojiMatch) {
            emoji = emojiMatch[1];
        }
        
        // Extract polarity
        const polarityMatch = content.match(/میزان احساس \(Polarity\): ([-\d.]+)/);
        if (polarityMatch) {
            polarity = polarityMatch[1];
        }
        
        // Extract subjectivity
        const subjectivityMatch = content.match(/میزان ذهنی‌بودن \(Subjectivity\): ([-\d.]+)/);
        if (subjectivityMatch) {
            subjectivity = subjectivityMatch[1];
        }

        // Create formatted display
        const resultHTML = `
            <div class="sentiment-result">
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center gap-3">
                        <span class="text-4xl">${emoji}</span>
                        <div>
                            <h3 class="text-xl font-bold text-gray-800">${sentiment}</h3>
                            <p class="text-sm text-gray-600">نتیجه تحلیل احساسات</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="bg-purple-100 px-3 py-1 rounded-full text-purple-800 text-sm font-medium">
                            Polarity: ${polarity}
                        </div>
                    </div>
                </div>
                
                <div class="bg-gray-50 p-3 rounded-lg mb-3">
                    <p class="text-sm text-gray-600 mb-1">متن تحلیل شده:</p>
                    <p class="text-gray-800 font-medium">"${originalText}"</p>
                </div>
                
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div class="bg-blue-50 p-3 rounded-lg">
                        <span class="text-blue-700 font-medium">میزان احساس</span>
                        <p class="text-blue-600">${polarity} (از -1 تا +1)</p>
                    </div>
                    <div class="bg-green-50 p-3 rounded-lg">
                        <span class="text-green-700 font-medium">میزان ذهنی‌بودن</span>
                        <p class="text-green-600">${subjectivity} (از 0 تا 1)</p>
                    </div>
                </div>
                
                <div class="mt-3 text-xs text-gray-500 border-t pt-2">
                    <p><strong>توضیح:</strong> مثبت (خوشحالی، رضایت) • منفی (ناراحتی، نارضایتی) • خنثی (بدون گرایش خاص)</p>
                </div>
            </div>
        `;

        this.sentimentContent.innerHTML = resultHTML;
        this.sentimentResult.classList.remove('hidden');
        
        // Clear input after successful analysis
        this.sentimentInput.value = '';
    }

    // Show/hide sentiment loading
    showSentimentLoading(show) {
        if (show) {
            this.sentimentLoading.classList.remove('hidden');
            this.sentimentResult.classList.add('hidden');
        } else {
            this.sentimentLoading.classList.add('hidden');
        }
    }

    // Summarize text
    async summarizeText() {
        const text = this.summaryInput.value.trim();
        if (!text) {
            this.showNotification('لطفاً متنی برای خلاصه‌سازی وارد کنید.', 'warning');
            return;
        }

        if (text.length < 50) {
            this.showNotification('متن باید حداقل 50 کاراکتر باشد.', 'warning');
            return;
        }

        this.showSummaryLoading(true);
        this.summaryBtn.disabled = true;

        try {
            // Prepare message for SummaryAgent
            const message = `خلاصه کن: ${text}`;
            
            const response = await fetch(`${this.apiBase}/agent/summary/public`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displaySummaryResult(data.content, text);
            } else {
                throw new Error(data.error || 'خطا در خلاصه‌سازی');
            }

        } catch (error) {
            console.error('Summarization error:', error);
            this.showNotification(`خطا در خلاصه‌سازی: ${error.message}`, 'error');
        } finally {
            this.showSummaryLoading(false);
            this.summaryBtn.disabled = false;
        }
    }

    // Display summarization result
    displaySummaryResult(content, originalText) {
        // Parse the content to extract summary info
        const lines = content.split('\n');
        let summaryText = content;
        let summaryId = '';
        let compression = '';
        let processingTime = '';
        
        // Extract main summary content (everything before the stats section)
        const statsIndex = content.indexOf('📊 **آمار خلاصه‌سازی:**');
        if (statsIndex > 0) {
            summaryText = content.substring(0, statsIndex).trim();
        }
        
        // Extract compression ratio
        const compressionMatch = content.match(/میزان فشرده‌سازی: ([\d.]+)%/);
        if (compressionMatch) {
            compression = compressionMatch[1];
        }
        
        // Extract processing time
        const timeMatch = content.match(/زمان پردازش: ([\d:]+)/);
        if (timeMatch) {
            processingTime = timeMatch[1];
        }
        
        // Extract summary ID
        const idMatch = content.match(/شناسه ذخیره: #(\d+)/);
        if (idMatch) {
            summaryId = idMatch[1];
        }

        // Create formatted display
        const resultHTML = `
            <div class="summary-result">
                <div class="mb-4">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-2xl">📝</span>
                        <h3 class="text-lg font-bold text-gray-800">خلاصه تولیدشده</h3>
                        ${summaryId ? `<span class="bg-emerald-100 text-emerald-800 text-xs px-2 py-1 rounded-full">#${summaryId}</span>` : ''}
                    </div>
                </div>
                
                <div class="bg-emerald-50 p-4 rounded-lg mb-4 border-l-4 border-emerald-500">
                    <div class="prose prose-sm max-w-none">
                        ${summaryText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>')}
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm mb-4">
                    <div class="bg-blue-50 p-3 rounded-lg">
                        <span class="text-blue-700 font-medium">متن اصلی</span>
                        <p class="text-blue-600">${originalText.length.toLocaleString()} کاراکتر</p>
                    </div>
                    ${compression ? `
                    <div class="bg-green-50 p-3 rounded-lg">
                        <span class="text-green-700 font-medium">فشرده‌سازی</span>
                        <p class="text-green-600">${compression}% کاهش حجم</p>
                    </div>
                    ` : ''}
                    ${processingTime ? `
                    <div class="bg-purple-50 p-3 rounded-lg">
                        <span class="text-purple-700 font-medium">زمان پردازش</span>
                        <p class="text-purple-600">${processingTime}</p>
                    </div>
                    ` : ''}
                </div>
                
                <div class="flex gap-2 mt-4">
                    <button 
                        onclick="copyToClipboard('${summaryText.replace(/'/g, "\\'").replace(/\n/g, '\\n')}')"
                        class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        📋 کپی خلاصه
                    </button>
                    <button 
                        onclick="clearSummaryResult()"
                        class="bg-emerald-500 hover:bg-emerald-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        🆕 خلاصه جدید
                    </button>
                </div>
                
                <div class="mt-3 text-xs text-gray-500 border-t pt-2">
                    <p><strong>نکته:</strong> این خلاصه با استفاده از هوش مصنوعی GPT-4o تولید شده و در دیتابیس ذخیره گردیده است.</p>
                </div>
            </div>
        `;

        this.summaryContent.innerHTML = resultHTML;
        this.summaryResult.classList.remove('hidden');
        
        // Clear input after successful summarization
        this.summaryInput.value = '';
    }

    // Show/hide summary loading
    showSummaryLoading(show) {
        if (show) {
            this.summaryLoading.classList.remove('hidden');
            this.summaryResult.classList.add('hidden');
        } else {
            this.summaryLoading.classList.add('hidden');
        }
    }

    // Copy text to clipboard
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('خلاصه کپی شد!', 'success');
        }).catch(err => {
            console.error('Copy failed:', err);
            this.showNotification('خطا در کپی کردن', 'error');
        });
    }

    // Clear summary result and prepare for new summarization
    clearSummaryResult() {
        this.summaryResult.classList.add('hidden');
        this.summaryInput.focus();
    }

    // Save memory to long-term storage
    async saveMemory() {
        const content = this.memoryInput.value.trim();
        const category = this.memoryCategory.value;
        const tags = this.memoryTags.value.trim();
        
        if (!content) {
            this.showNotification('لطفاً محتوای حافظه را وارد کنید.', 'warning');
            return;
        }

        this.showMemoryLoading(true);
        this.saveMemoryBtn.disabled = true;

        try {
            // Prepare message with category and tags
            let message = content;
            if (category !== 'یادداشت') {
                message = `${category}: ${content}`;
            }
            if (tags) {
                message += ` ${tags}`;
            }
            
            const response = await fetch(`${this.apiBase}/agent/longterm/save/public`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ 
                    message: message,
                    context: {
                        category: category,
                        tags: tags
                    }
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayMemoryResult(data.content, 'save');
                // Clear inputs after successful save
                this.memoryInput.value = '';
                this.memoryTags.value = '';
                this.memoryCategory.value = 'یادداشت';
            } else {
                throw new Error(data.error || 'خطا در ذخیره حافظه');
            }

        } catch (error) {
            console.error('Memory save error:', error);
            this.showNotification(`خطا در ذخیره حافظه: ${error.message}`, 'error');
        } finally {
            this.showMemoryLoading(false);
            this.saveMemoryBtn.disabled = false;
        }
    }

    // Fetch recent memories
    async fetchMemories() {
        this.showMemoryLoading(true);
        this.fetchMemoriesBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/agent/longterm/fetch/public`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                mode: 'cors'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayMemoryResult(data.content, 'fetch');
            } else {
                throw new Error(data.error || 'خطا در دریافت حافظه‌ها');
            }

        } catch (error) {
            console.error('Memory fetch error:', error);
            this.showNotification(`خطا در دریافت حافظه‌ها: ${error.message}`, 'error');
        } finally {
            this.showMemoryLoading(false);
            this.fetchMemoriesBtn.disabled = false;
        }
    }

    // Display memory operation result
    displayMemoryResult(content, operation) {
        const resultHTML = `
            <div class="memory-result">
                <div class="mb-4">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-2xl">${operation === 'save' ? '💾' : '📚'}</span>
                        <h3 class="text-lg font-bold text-gray-800">
                            ${operation === 'save' ? 'نتیجه ذخیره‌سازی' : 'حافظه‌های ذخیره شده'}
                        </h3>
                    </div>
                </div>
                
                <div class="bg-purple-50 p-4 rounded-lg border-l-4 border-purple-500">
                    <div class="prose prose-sm max-w-none text-right">
                        ${content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>')}
                    </div>
                </div>
                
                <div class="flex gap-2 mt-4">
                    <button 
                        onclick="copyMemoryToClipboard('${content.replace(/'/g, "\\'").replace(/\n/g, '\\n')}')"
                        class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        📋 کپی محتوا
                    </button>
                    <button 
                        onclick="clearMemoryResult()"
                        class="bg-purple-500 hover:bg-purple-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        🆕 عملیات جدید
                    </button>
                </div>
                
                <div class="mt-3 text-xs text-gray-500 border-t pt-2">
                    <p><strong>نکته:</strong> حافظه‌ها در دیتابیس PostgreSQL ذخیره شده و قابل جستجو هستند.</p>
                </div>
            </div>
        `;

        this.memoryContent.innerHTML = resultHTML;
        this.memoryResult.classList.remove('hidden');
    }

    // Show/hide memory loading
    showMemoryLoading(show) {
        if (show) {
            this.memoryLoading.classList.remove('hidden');
            this.memoryResult.classList.add('hidden');
        } else {
            this.memoryLoading.classList.add('hidden');
        }
    }

    // Copy memory content to clipboard
    copyMemoryToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('محتوا کپی شد!', 'success');
        }).catch(err => {
            console.error('Copy failed:', err);
            this.showNotification('خطا در کپی کردن', 'error');
        });
    }

    // Clear memory result and prepare for new operation
    clearMemoryResult() {
        this.memoryResult.classList.add('hidden');
        this.memoryInput.focus();
    }

    // Analyze conceptual content
    async analyzeConcept() {
        const content = this.conceptualInput.value.trim();
        
        if (!content) {
            this.showNotification('لطفاً جمله یا مفهوم خود را وارد کنید.', 'warning');
            return;
        }

        this.showConceptualLoading(true);
        this.analyzeConceptBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/agent/conceptual/save/public`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ 
                    message: content,
                    context: {}
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayConceptualResult(data.content, 'analyze');
                // Clear input after successful analysis
                this.conceptualInput.value = '';
            } else {
                throw new Error(data.error || 'خطا در تحلیل مفهوم');
            }

        } catch (error) {
            console.error('Conceptual analysis error:', error);
            this.showNotification(`خطا در تحلیل مفهوم: ${error.message}`, 'error');
        } finally {
            this.showConceptualLoading(false);
            this.analyzeConceptBtn.disabled = false;
        }
    }

    // Fetch latest conceptual memories
    async fetchLatestConcepts() {
        this.showConceptualLoading(true);
        this.fetchConceptsBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/agent/conceptual/latest/public`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                mode: 'cors'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayConceptualResult(data.content, 'latest');
            } else {
                throw new Error(data.error || 'خطا در دریافت مفاهیم');
            }

        } catch (error) {
            console.error('Conceptual fetch error:', error);
            this.showNotification(`خطا در دریافت مفاهیم: ${error.message}`, 'error');
        } finally {
            this.showConceptualLoading(false);
            this.fetchConceptsBtn.disabled = false;
        }
    }

    // Display conceptual analysis result
    displayConceptualResult(content, operation) {
        const resultHTML = `
            <div class="conceptual-result">
                <div class="mb-4">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-2xl">${operation === 'analyze' ? '🧠' : '📊'}</span>
                        <h3 class="text-lg font-bold text-gray-800">
                            ${operation === 'analyze' ? 'نتیجه تحلیل مفهومی' : 'آخرین مفاهیم تحلیل شده'}
                        </h3>
                    </div>
                </div>
                
                <div class="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
                    <div class="prose prose-sm max-w-none text-right conceptual-content">
                        ${this.formatConceptualContent(content)}
                    </div>
                </div>
                
                <div class="flex gap-2 mt-4">
                    <button 
                        onclick="copyConceptualToClipboard('${content.replace(/'/g, "\\'").replace(/\n/g, '\\n')}')"
                        class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        📋 کپی محتوا
                    </button>
                    <button 
                        onclick="clearConceptualResult()"
                        class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        🆕 تحلیل جدید
                    </button>
                </div>
                
                <div class="mt-3 text-xs text-gray-500 border-t pt-2">
                    <p><strong>نکته:</strong> تحلیل مفهومی با OpenAI GPT یا keyword detection انجام می‌شود.</p>
                </div>
            </div>
        `;

        this.conceptualContent.innerHTML = resultHTML;
        this.conceptualResult.classList.remove('hidden');
    }

    // Format conceptual content with enhanced styling
    formatConceptualContent(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong class="text-blue-800">$1</strong>')
            .replace(/🎯/g, '<span class="text-orange-500">🎯</span>')
            .replace(/💎/g, '<span class="text-purple-500">💎</span>')
            .replace(/📚/g, '<span class="text-green-500">📚</span>')
            .replace(/⭐/g, '<span class="text-yellow-500">⭐</span>')
            .replace(/😰/g, '<span class="text-red-500">😰</span>')
            .replace(/💪/g, '<span class="text-blue-500">💪</span>')
            .replace(/😟/g, '<span class="text-gray-500">😟</span>')
            .replace(/✨/g, '<span class="text-pink-500">✨</span>')
            .replace(/😊/g, '<span class="text-green-500">😊</span>')
            .replace(/😔/g, '<span class="text-red-500">😔</span>')
            .replace(/😐/g, '<span class="text-gray-500">😐</span>')
            .replace(/\n/g, '<br>');
    }

    // Show/hide conceptual loading
    showConceptualLoading(show) {
        if (show) {
            this.conceptualLoading.classList.remove('hidden');
            this.conceptualResult.classList.add('hidden');
        } else {
            this.conceptualLoading.classList.add('hidden');
        }
    }

    // Copy conceptual content to clipboard
    copyConceptualToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('محتوا کپی شد!', 'success');
        }).catch(err => {
            console.error('Copy failed:', err);
            this.showNotification('خطا در کپی کردن', 'error');
        });
    }

    // Clear conceptual result and prepare for new analysis
    clearConceptualResult() {
        this.conceptualResult.classList.add('hidden');
        this.conceptualInput.focus();
    }

    // Observe repetitive pattern
    async observeRepetitivePattern() {
        const content = this.repetitiveInput.value.trim();
        
        if (!content) {
            this.showNotification('لطفاً متن خود را برای تحلیل الگو وارد کنید.', 'warning');
            return;
        }

        this.showRepetitiveLoading(true);
        this.observePatternBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/agent/repetitive/observe/public`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ 
                    message: content,
                    context: {}
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayRepetitiveResult(data.content, 'observe');
                // Clear input after successful analysis
                this.repetitiveInput.value = '';
            } else {
                throw new Error(data.error || 'خطا در تحلیل الگوی تکراری');
            }

        } catch (error) {
            console.error('Repetitive pattern analysis error:', error);
            this.showNotification(`خطا در تحلیل الگو: ${error.message}`, 'error');
        } finally {
            this.showRepetitiveLoading(false);
            this.observePatternBtn.disabled = false;
        }
    }

    // Fetch frequent repetitive patterns
    async fetchFrequentPatterns() {
        this.showRepetitiveLoading(true);
        this.fetchPatternsBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/agent/repetitive/frequent/public`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                mode: 'cors'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayRepetitiveResult(data.content, 'frequent');
            } else {
                throw new Error(data.error || 'خطا در دریافت الگوهای تکراری');
            }

        } catch (error) {
            console.error('Frequent patterns fetch error:', error);
            this.showNotification(`خطا در دریافت الگوها: ${error.message}`, 'error');
        } finally {
            this.showRepetitiveLoading(false);
            this.fetchPatternsBtn.disabled = false;
        }
    }

    // Display repetitive pattern analysis result
    displayRepetitiveResult(content, operation) {
        const resultHTML = `
            <div class="repetitive-result">
                <div class="mb-4">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-2xl">${operation === 'observe' ? '🔍' : '📊'}</span>
                        <h3 class="text-lg font-bold text-gray-800">
                            ${operation === 'observe' ? 'نتیجه تحلیل الگوی تکراری' : 'الگوهای تکراری شناسایی شده'}
                        </h3>
                    </div>
                </div>
                
                <div class="bg-purple-50 p-4 rounded-lg border-l-4 border-purple-500">
                    <div class="prose prose-sm max-w-none text-right repetitive-content">
                        ${this.formatRepetitiveContent(content)}
                    </div>
                </div>
                
                <div class="flex gap-2 mt-4">
                    <button 
                        onclick="copyRepetitiveToClipboard('${content.replace(/'/g, "\\'").replace(/\n/g, '\\n')}')"
                        class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        📋 کپی محتوا
                    </button>
                    <button 
                        onclick="clearRepetitiveResult()"
                        class="bg-purple-500 hover:bg-purple-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        🆕 تحلیل جدید
                    </button>
                </div>
                
                <div class="mt-3 text-xs text-gray-500 border-t pt-2">
                    <p><strong>نکته:</strong> سیستم الگوهای تکراری را تشخیص داده و در دیتابیس ذخیره می‌کند.</p>
                </div>
            </div>
        `;

        this.repetitiveContent.innerHTML = resultHTML;
        this.repetitiveResult.classList.remove('hidden');
    }

    // Format repetitive content with enhanced styling
    formatRepetitiveContent(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong class="text-purple-800">$1</strong>')
            .replace(/🚨/g, '<span class="text-red-600">🚨</span>')
            .replace(/⚠️/g, '<span class="text-yellow-500">⚠️</span>')
            .replace(/📝/g, '<span class="text-blue-500">📝</span>')
            .replace(/🎯/g, '<span class="text-orange-500">🎯</span>')
            .replace(/😟/g, '<span class="text-gray-500">😟</span>')
            .replace(/❤️/g, '<span class="text-red-500">❤️</span>')
            .replace(/🔄/g, '<span class="text-purple-500">🔄</span>')
            .replace(/🔁/g, '<span class="text-pink-500">🔁</span>')
            .replace(/\n/g, '<br>');
    }

    // Show/hide repetitive loading
    showRepetitiveLoading(show) {
        if (show) {
            this.repetitiveLoading.classList.remove('hidden');
            this.repetitiveResult.classList.add('hidden');
        } else {
            this.repetitiveLoading.classList.add('hidden');
        }
    }

    // Copy repetitive content to clipboard
    copyRepetitiveToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('محتوا کپی شد!', 'success');
        }).catch(err => {
            console.error('Copy failed:', err);
            this.showNotification('خطا در کپی کردن', 'error');
        });
    }

    // Clear repetitive result and prepare for new analysis
    clearRepetitiveResult() {
        this.repetitiveResult.classList.add('hidden');
        this.repetitiveInput.focus();
    }

    // Build knowledge graph
    async buildKnowledgeGraph() {
        const content = this.knowledgeGraphInput.value.trim();
        
        if (!content) {
            this.showNotification('لطفاً متن خود را برای تحلیل مفاهیم وارد کنید.', 'warning');
            return;
        }

        this.showKnowledgeGraphLoading(true);
        this.buildGraphBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/agent/knowledge-graph/build/public`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ 
                    message: content,
                    context: {}
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayKnowledgeGraphResult(data.content, 'build');
                // Clear input after successful analysis
                this.knowledgeGraphInput.value = '';
            } else {
                throw new Error(data.error || 'خطا در ساخت گراف دانش');
            }

        } catch (error) {
            console.error('Knowledge graph build error:', error);
            this.showNotification(`خطا در ساخت گراف: ${error.message}`, 'error');
        } finally {
            this.showKnowledgeGraphLoading(false);
            this.buildGraphBtn.disabled = false;
        }
    }

    // List knowledge graphs
    async listKnowledgeGraphs() {
        this.showKnowledgeGraphLoading(true);
        this.listGraphsBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/agent/knowledge-graph/list/public`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                mode: 'cors'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayKnowledgeGraphResult(data.content, 'list');
            } else {
                throw new Error(data.error || 'خطا در نمایش گراف‌های دانش');
            }

        } catch (error) {
            console.error('Knowledge graphs list error:', error);
            this.showNotification(`خطا در نمایش گراف‌ها: ${error.message}`, 'error');
        } finally {
            this.showKnowledgeGraphLoading(false);
            this.listGraphsBtn.disabled = false;
        }
    }

    // Display knowledge graph result
    displayKnowledgeGraphResult(content, operation) {
        const resultHTML = `
            <div class="knowledge-graph-result">
                <div class="mb-4">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-2xl">${operation === 'build' ? '🧠' : '📚'}</span>
                        <h3 class="text-lg font-bold text-gray-800">
                            ${operation === 'build' ? 'گراف دانش ساخته شد' : 'گراف‌های دانش ذخیره شده'}
                        </h3>
                    </div>
                </div>
                
                <div class="bg-indigo-50 p-4 rounded-lg border-l-4 border-indigo-500">
                    <div class="prose prose-sm max-w-none text-right knowledge-graph-content">
                        ${this.formatKnowledgeGraphContent(content)}
                    </div>
                </div>
                
                <div class="flex gap-2 mt-4">
                    <button 
                        onclick="copyKnowledgeGraphToClipboard('${content.replace(/'/g, "\\'").replace(/\n/g, '\\n')}')"
                        class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        📋 کپی محتوا
                    </button>
                    <button 
                        onclick="clearKnowledgeGraphResult()"
                        class="bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        🆕 تحلیل جدید
                    </button>
                </div>
                
                <div class="mt-3 text-xs text-gray-500 border-t pt-2">
                    <p><strong>نکته:</strong> گراف‌های دانش شامل مفاهیم و روابط استخراج شده از متن هستند.</p>
                </div>
            </div>
        `;

        this.knowledgeGraphContent.innerHTML = resultHTML;
        this.knowledgeGraphResult.classList.remove('hidden');
    }

    // Format knowledge graph content with enhanced styling
    formatKnowledgeGraphContent(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong class="text-indigo-800">$1</strong>')
            .replace(/🧠/g, '<span class="text-purple-600">🧠</span>')
            .replace(/📊/g, '<span class="text-blue-500">📊</span>')
            .replace(/🔗/g, '<span class="text-green-500">🔗</span>')
            .replace(/📈/g, '<span class="text-orange-500">📈</span>')
            .replace(/🎯/g, '<span class="text-red-500">🎯</span>')
            .replace(/💡/g, '<span class="text-yellow-500">💡</span>')
            .replace(/⚙️/g, '<span class="text-gray-600">⚙️</span>')
            .replace(/👤/g, '<span class="text-pink-500">👤</span>')
            .replace(/📍/g, '<span class="text-green-600">📍</span>')
            .replace(/💭/g, '<span class="text-indigo-500">💭</span>')
            .replace(/\n/g, '<br>');
    }

    // Show/hide knowledge graph loading
    showKnowledgeGraphLoading(show) {
        if (show) {
            this.knowledgeGraphLoading.classList.remove('hidden');
            this.knowledgeGraphResult.classList.add('hidden');
        } else {
            this.knowledgeGraphLoading.classList.add('hidden');
        }
    }

    // Copy knowledge graph content to clipboard
    copyKnowledgeGraphToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('محتوا کپی شد!', 'success');
        }).catch(err => {
            console.error('Copy failed:', err);
            this.showNotification('خطا در کپی کردن', 'error');
        });
    }

    // Clear knowledge graph result and prepare for new analysis
    clearKnowledgeGraphResult() {
        this.knowledgeGraphResult.classList.add('hidden');
        this.knowledgeGraphInput.focus();
    }

    // Get text completion suggestions
    async getCompletion() {
        const content = this.suggesterInput.value.trim();
        
        if (!content) {
            this.showNotification('لطفاً متن خود را برای دریافت پیشنهادات ادامه وارد کنید.', 'warning');
            return;
        }

        this.showSuggesterLoading(true);
        this.getCompletionBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/agent/suggester/complete/public`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ 
                    message: content,
                    context: {}
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displaySuggesterResult(data.content, 'completion');
            } else {
                throw new Error(data.error || 'خطا در تولید پیشنهادات ادامه');
            }

        } catch (error) {
            console.error('Completion suggestion error:', error);
            this.showNotification(`خطا در تولید ادامه: ${error.message}`, 'error');
        } finally {
            this.showSuggesterLoading(false);
            this.getCompletionBtn.disabled = false;
        }
    }

    // Get contextual hints
    async getHints() {
        this.showSuggesterLoading(true);
        this.getHintsBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/agent/suggester/hints/public`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                mode: 'cors'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displaySuggesterResult(data.content, 'hints');
            } else {
                throw new Error(data.error || 'خطا در تولید راهنماها');
            }

        } catch (error) {
            console.error('Hints error:', error);
            this.showNotification(`خطا در تولید راهنماها: ${error.message}`, 'error');
        } finally {
            this.showSuggesterLoading(false);
            this.getHintsBtn.disabled = false;
        }
    }

    // Get comprehensive smart suggestions
    async getSmartSuggestions() {
        const content = this.suggesterInput.value.trim();
        
        if (!content) {
            this.showNotification('لطفاً متن خود را برای دریافت پیشنهادات هوشمند وارد کنید.', 'warning');
            return;
        }

        this.showSuggesterLoading(true);
        this.getSmartSuggestionsBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/agent/public`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ 
                    message: `پیشنهاد: ${content}`,
                    context: {}
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displaySuggesterResult(data.content, 'smart');
            } else {
                throw new Error(data.error || 'خطا در تولید پیشنهادات هوشمند');
            }

        } catch (error) {
            console.error('Smart suggestions error:', error);
            this.showNotification(`خطا در تولید پیشنهادات: ${error.message}`, 'error');
        } finally {
            this.showSuggesterLoading(false);
            this.getSmartSuggestionsBtn.disabled = false;
        }
    }

    // Display suggester result
    displaySuggesterResult(content, operation) {
        const resultHTML = `
            <div class="suggester-result">
                <div class="mb-4">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-2xl">${operation === 'completion' ? '➡️' : operation === 'hints' ? '💡' : '🚀'}</span>
                        <h3 class="text-lg font-bold text-gray-800">
                            ${operation === 'completion' ? 'پیشنهادات ادامه' : operation === 'hints' ? 'راهنماهای زمینه‌ای' : 'پیشنهادات هوشمند'}
                        </h3>
                    </div>
                </div>
                
                <div class="bg-purple-50 p-4 rounded-lg border-l-4 border-purple-500">
                    <div class="prose prose-sm max-w-none text-right suggester-content">
                        ${this.formatSuggesterContent(content)}
                    </div>
                </div>
                
                <div class="flex gap-2 mt-4">
                    <button 
                        onclick="copySuggesterToClipboard('${content.replace(/'/g, "\\'").replace(/\n/g, '\\n')}')"
                        class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        📋 کپی محتوا
                    </button>
                    <button 
                        onclick="clearSuggesterResult()"
                        class="bg-purple-500 hover:bg-purple-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        🆕 پیشنهاد جدید
                    </button>
                </div>
                
                <div class="mt-3 text-xs text-gray-500 border-t pt-2">
                    <p><strong>نکته:</strong> پیشنهادات بر اساس تحلیل زمینه و حافظه شما تولید شده‌اند.</p>
                </div>
            </div>
        `;

        this.suggesterContent.innerHTML = resultHTML;
        this.suggesterResult.classList.remove('hidden');
    }

    // Format suggester content with enhanced styling
    formatSuggesterContent(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong class="text-purple-800">$1</strong>')
            .replace(/✨/g, '<span class="text-yellow-500">✨</span>')
            .replace(/🔮/g, '<span class="text-purple-600">🔮</span>')
            .replace(/🚀/g, '<span class="text-blue-500">🚀</span>')
            .replace(/➡️/g, '<span class="text-green-500">➡️</span>')
            .replace(/⚡/g, '<span class="text-yellow-600">⚡</span>')
            .replace(/⚠️/g, '<span class="text-red-500">⚠️</span>')
            .replace(/🔗/g, '<span class="text-indigo-500">🔗</span>')
            .replace(/📈/g, '<span class="text-green-600">📈</span>')
            .replace(/🎯/g, '<span class="text-red-600">🎯</span>')
            .replace(/💡/g, '<span class="text-yellow-500">💡</span>')
            .replace(/🟢/g, '<span class="text-green-500">🟢</span>')
            .replace(/🟡/g, '<span class="text-yellow-500">🟡</span>')
            .replace(/🔵/g, '<span class="text-blue-500">🔵</span>')
            .replace(/\n/g, '<br>');
    }

    // Show/hide suggester loading
    showSuggesterLoading(show) {
        if (show) {
            this.suggesterLoading.classList.remove('hidden');
            this.suggesterResult.classList.add('hidden');
        } else {
            this.suggesterLoading.classList.add('hidden');
        }
    }

    // Copy suggester content to clipboard
    copySuggesterToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('محتوا کپی شد!', 'success');
        }).catch(err => {
            console.error('Copy failed:', err);
            this.showNotification('خطا در کپی کردن', 'error');
        });
    }

    // Clear suggester result and prepare for new suggestions
    clearSuggesterResult() {
        this.suggesterResult.classList.add('hidden');
        this.suggesterInput.focus();
    }

    // Analyze goal and intent
    async analyzeGoal() {
        const content = this.goalInferenceInput.value.trim();
        
        if (!content) {
            this.showNotification('لطفاً متن خود را برای تحلیل هدف وارد کنید.', 'warning');
            return;
        }

        this.showGoalInferenceLoading(true);
        this.analyzeGoalBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/agent/goal-inference/analyze/public`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ 
                    message: content,
                    context: {}
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayGoalInferenceResult(data.content);
            } else {
                throw new Error(data.error || 'خطا در تحلیل هدف و نیت');
            }

        } catch (error) {
            console.error('Goal inference error:', error);
            this.showNotification(`خطا در تحلیل هدف: ${error.message}`, 'error');
        } finally {
            this.showGoalInferenceLoading(false);
            this.analyzeGoalBtn.disabled = false;
        }
    }

    // Display goal inference result
    displayGoalInferenceResult(content) {
        const resultHTML = `
            <div class="goal-inference-result">
                <div class="mb-4">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-2xl">🎯</span>
                        <h3 class="text-lg font-bold text-gray-800">تحلیل هدف و نیت</h3>
                    </div>
                </div>
                
                <div class="bg-indigo-50 p-4 rounded-lg border-l-4 border-indigo-500">
                    <div class="prose prose-sm max-w-none text-right goal-content">
                        ${this.formatGoalInferenceContent(content)}
                    </div>
                </div>
                
                <div class="flex gap-2 mt-4">
                    <button 
                        onclick="copyGoalAnalysisToClipboard('${content.replace(/'/g, "\\'").replace(/\n/g, '\\n')}')"
                        class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        📋 کپی نتیجه
                    </button>
                    <button 
                        onclick="clearGoalAnalysis()"
                        class="bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        🆕 تحلیل جدید
                    </button>
                </div>
                
                <div class="mt-3 text-xs text-gray-500 border-t pt-2">
                    <p><strong>نکته:</strong> تحلیل بر اساس الگوها و زمینه پیام شما انجام شده است.</p>
                </div>
            </div>
        `;

        this.goalInferenceContent.innerHTML = resultHTML;
        this.goalInferenceResult.classList.remove('hidden');
    }

    // Format goal inference content with enhanced styling
    formatGoalInferenceContent(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong class="text-indigo-800">$1</strong>')
            .replace(/```json\n([\s\S]*?)\n```/g, '<pre class="bg-gray-100 p-3 rounded text-sm overflow-x-auto border"><code>$1</code></pre>')
            .replace(/🎯/g, '<span class="text-indigo-600">🎯</span>')
            .replace(/🚀/g, '<span class="text-blue-500">🚀</span>')
            .replace(/🤔/g, '<span class="text-yellow-600">🤔</span>')
            .replace(/😟/g, '<span class="text-red-500">😟</span>')
            .replace(/💪/g, '<span class="text-green-600">💪</span>')
            .replace(/❓/g, '<span class="text-purple-500">❓</span>')
            .replace(/📋/g, '<span class="text-gray-600">📋</span>')
            .replace(/📚/g, '<span class="text-blue-600">📚</span>')
            .replace(/🟢/g, '<span class="text-green-500">🟢</span>')
            .replace(/🟡/g, '<span class="text-yellow-500">🟡</span>')
            .replace(/🔴/g, '<span class="text-red-500">🔴</span>')
            .replace(/🔍/g, '<span class="text-indigo-500">🔍</span>')
            .replace(/🧠/g, '<span class="text-purple-600">🧠</span>')
            .replace(/🤖/g, '<span class="text-blue-500">🤖</span>')
            .replace(/💡/g, '<span class="text-yellow-500">💡</span>')
            .replace(/\n/g, '<br>');
    }

    // Show/hide goal inference loading
    showGoalInferenceLoading(show) {
        if (show) {
            this.goalInferenceLoading.classList.remove('hidden');
            this.goalInferenceResult.classList.add('hidden');
        } else {
            this.goalInferenceLoading.classList.add('hidden');
        }
    }

    // Copy goal analysis to clipboard
    copyGoalAnalysisToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('نتیجه تحلیل کپی شد!', 'success');
        }).catch(err => {
            console.error('Copy failed:', err);
            this.showNotification('خطا در کپی کردن', 'error');
        });
    }

    // Clear goal analysis and prepare for new input
    clearGoalAnalysis() {
        this.goalInferenceResult.classList.add('hidden');
        this.goalInferenceInput.value = '';
        this.goalInferenceInput.focus();
    }

    // Analyze emotion and provide regulation suggestions
    async analyzeEmotion() {
        const content = this.emotionInput.value.trim();
        
        if (!content) {
            this.showNotification('لطفاً احساس یا هیجان خود را برای تحلیل وارد کنید.', 'warning');
            return;
        }

        this.showEmotionLoading(true);
        this.analyzeEmotionBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/agent/emotion-regulation/analyze/public`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ 
                    message: content,
                    context: {}
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayEmotionResult(data.content);
            } else {
                throw new Error(data.error || 'خطا در تحلیل هیجان');
            }

        } catch (error) {
            console.error('Emotion analysis error:', error);
            this.showNotification(`خطا در تحلیل هیجان: ${error.message}`, 'error');
        } finally {
            this.showEmotionLoading(false);
            this.analyzeEmotionBtn.disabled = false;
        }
    }

    // Display emotion analysis result
    displayEmotionResult(content) {
        const resultHTML = `
            <div class="emotion-analysis-result">
                <div class="mb-4">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-2xl">💝</span>
                        <h3 class="text-lg font-bold text-gray-800">تحلیل و تنظیم هیجان</h3>
                    </div>
                </div>
                
                <div class="bg-pink-50 p-4 rounded-lg border-l-4 border-pink-500">
                    <div class="prose prose-sm max-w-none text-right emotion-content">
                        ${this.formatEmotionContent(content)}
                    </div>
                </div>
                
                <div class="flex gap-2 mt-4">
                    <button 
                        onclick="copyEmotionAnalysisToClipboard('${content.replace(/'/g, "\\'").replace(/\n/g, '\\n')}')"
                        class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        📋 کپی نتیجه
                    </button>
                    <button 
                        onclick="clearEmotionAnalysis()"
                        class="bg-pink-500 hover:bg-pink-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        🆕 تحلیل جدید
                    </button>
                </div>
                
                <div class="mt-3 text-xs text-gray-500 border-t pt-2">
                    <p><strong>نکته:</strong> این تحلیل بر اساس محتوای پیام و الگوهای احساسی شما انجام شده است.</p>
                </div>
            </div>
        `;

        this.emotionContent.innerHTML = resultHTML;
        this.emotionResult.classList.remove('hidden');
    }

    // Format emotion content with enhanced styling
    formatEmotionContent(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong class="text-pink-800">$1</strong>')
            .replace(/```json\n([\s\S]*?)\n```/g, '<pre class="bg-gray-100 p-3 rounded text-sm overflow-x-auto border"><code>$1</code></pre>')
            .replace(/💝/g, '<span class="text-pink-600">💝</span>')
            .replace(/😠/g, '<span class="text-red-500">😠</span>')
            .replace(/😤/g, '<span class="text-orange-500">😤</span>')
            .replace(/😰/g, '<span class="text-blue-500">😰</span>')
            .replace(/😄/g, '<span class="text-yellow-500">😄</span>')
            .replace(/😕/g, '<span class="text-gray-500">😕</span>')
            .replace(/😊/g, '<span class="text-green-500">😊</span>')
            .replace(/😁/g, '<span class="text-green-600">😁</span>')
            .replace(/😢/g, '<span class="text-blue-600">😢</span>')
            .replace(/😫/g, '<span class="text-purple-500">😫</span>')
            .replace(/😨/g, '<span class="text-indigo-500">😨</span>')
            .replace(/🤗/g, '<span class="text-yellow-600">🤗</span>')
            .replace(/😐/g, '<span class="text-gray-400">😐</span>')
            .replace(/🟢/g, '<span class="text-green-500">🟢</span>')
            .replace(/🟡/g, '<span class="text-yellow-500">🟡</span>')
            .replace(/🔴/g, '<span class="text-red-500">🔴</span>')
            .replace(/🔵/g, '<span class="text-blue-500">🔵</span>')
            .replace(/🟠/g, '<span class="text-orange-500">🟠</span>')
            .replace(/🎯/g, '<span class="text-indigo-600">🎯</span>')
            .replace(/⚠️/g, '<span class="text-yellow-600">⚠️</span>')
            .replace(/💡/g, '<span class="text-yellow-500">💡</span>')
            .replace(/\n/g, '<br>');
    }

    // Show/hide emotion loading
    showEmotionLoading(show) {
        if (show) {
            this.emotionLoading.classList.remove('hidden');
            this.emotionResult.classList.add('hidden');
        } else {
            this.emotionLoading.classList.add('hidden');
        }
    }

    // Copy emotion analysis to clipboard
    copyEmotionAnalysisToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('نتیجه تحلیل هیجان کپی شد!', 'success');
        }).catch(err => {
            console.error('Copy failed:', err);
            this.showNotification('خطا در کپی کردن', 'error');
        });
    }

    // Clear emotion analysis and prepare for new input
    clearEmotionAnalysis() {
        this.emotionResult.classList.add('hidden');
        this.emotionInput.value = '';
        this.emotionInput.focus();
    }

    // Analyze decision with multi-dimensional assessment
    async analyzeDecision() {
        const content = this.decisionInput.value.trim();
        
        if (!content) {
            this.showNotification('لطفاً تصمیم یا انتخاب خود را برای تحلیل وارد کنید.', 'warning');
            return;
        }

        this.showDecisionLoading(true);
        this.analyzeDecisionBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/agent/decision-support/analyze/public`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ 
                    message: content,
                    context: {}
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayDecisionResult(data.content);
            } else {
                throw new Error(data.error || 'خطا در تحلیل تصمیم');
            }

        } catch (error) {
            console.error('Decision analysis error:', error);
            this.showNotification(`خطا در تحلیل تصمیم: ${error.message}`, 'error');
        } finally {
            this.showDecisionLoading(false);
            this.analyzeDecisionBtn.disabled = false;
        }
    }

    // Display decision analysis result
    displayDecisionResult(content) {
        const resultHTML = `
            <div class="decision-analysis-result">
                <div class="mb-4">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-2xl">🎯</span>
                        <h3 class="text-lg font-bold text-gray-800">تحلیل پشتیبانی تصمیم</h3>
                    </div>
                </div>
                
                <div class="bg-purple-50 p-4 rounded-lg border-l-4 border-purple-500">
                    <div class="prose prose-sm max-w-none text-right decision-content">
                        ${this.formatDecisionContent(content)}
                    </div>
                </div>
                
                <div class="flex gap-2 mt-4">
                    <button 
                        onclick="copyDecisionAnalysisToClipboard('${content.replace(/'/g, "\\'").replace(/\n/g, '\\n')}')"
                        class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        📋 کپی نتیجه
                    </button>
                    <button 
                        onclick="clearDecisionAnalysis()"
                        class="bg-purple-500 hover:bg-purple-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        🆕 تحلیل جدید
                    </button>
                    <button 
                        onclick="listRecentDecisions()"
                        class="bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        📋 تصمیمات قبلی
                    </button>
                </div>
                
                <div class="mt-3 text-xs text-gray-500 border-t pt-2">
                    <p><strong>نکته:</strong> این تحلیل بر اساس هدف، احساس، حافظه و ریسک انجام شده است.</p>
                </div>
            </div>
        `;

        this.decisionContent.innerHTML = resultHTML;
        this.decisionResult.classList.remove('hidden');
    }

    // Format decision content with enhanced styling
    formatDecisionContent(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong class="text-purple-800">$1</strong>')
            .replace(/```json\n([\s\S]*?)\n```/g, '<pre class="bg-gray-100 p-3 rounded text-sm overflow-x-auto border"><code>$1</code></pre>')
            .replace(/🎯/g, '<span class="text-purple-600">🎯</span>')
            .replace(/🟢/g, '<span class="text-green-500">🟢</span>')
            .replace(/🟡/g, '<span class="text-yellow-500">🟡</span>')
            .replace(/🔴/g, '<span class="text-red-500">🔴</span>')
            .replace(/💝/g, '<span class="text-pink-600">💝</span>')
            .replace(/📊/g, '<span class="text-blue-600">📊</span>')
            .replace(/📈/g, '<span class="text-green-600">📈</span>')
            .replace(/⚠️/g, '<span class="text-yellow-600">⚠️</span>')
            .replace(/🧠/g, '<span class="text-indigo-600">🧠</span>')
            .replace(/█/g, '<span class="text-green-500">█</span>')
            .replace(/░/g, '<span class="text-gray-300">░</span>')
            .replace(/\n/g, '<br>');
    }

    // Show/hide decision loading
    showDecisionLoading(show) {
        if (show) {
            this.decisionLoading.classList.remove('hidden');
            this.decisionResult.classList.add('hidden');
        } else {
            this.decisionLoading.classList.add('hidden');
        }
    }

    // Copy decision analysis to clipboard
    copyDecisionAnalysisToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('نتیجه تحلیل تصمیم کپی شد!', 'success');
        }).catch(err => {
            console.error('Copy failed:', err);
            this.showNotification('خطا در کپی کردن', 'error');
        });
    }

    // Clear decision analysis and prepare for new input
    clearDecisionAnalysis() {
        this.decisionResult.classList.add('hidden');
        this.decisionInput.value = '';
        this.decisionInput.focus();
    }

    // Analyze reward/progress
    async analyzeReward() {
        const input = this.rewardInput.value.trim();
        if (!input) {
            this.showNotification('لطفاً وضعیت یا پیشرفت خود را وارد کنید.', 'warning');
            return;
        }

        this.analyzeRewardBtn.disabled = true;
        this.rewardLoading.classList.remove('hidden');
        this.rewardResult.classList.add('hidden');

        try {
            const response = await fetch('/agent/reward/analyze/public', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: input,
                    context: {}
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            this.rewardLoading.classList.add('hidden');
            this.rewardResult.classList.remove('hidden');
            
            // Display reward analysis result
            this.rewardContent.innerHTML = `
                <div class="whitespace-pre-wrap font-mono text-sm text-gray-800 rtl">
                    ${data.content}
                </div>
                <div class="mt-3 flex gap-2">
                    <button 
                        onclick="copyRewardAnalysisToClipboard(\`${data.content.replace(/`/g, '\\`')}\`)"
                        class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm"
                    >
                        📋 کپی
                    </button>
                    <button 
                        onclick="shareRewardAnalysis(\`${data.content.replace(/`/g, '\\`')}\`)"
                        class="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm"
                    >
                        🔗 اشتراک
                    </button>
                </div>
            `;
            
            // Show success notification based on reward detection
            if (data.success && data.content.includes('🏆')) {
                this.showNotification('🎉 تبریک! پیشرفت مثبت شما تشخیص داده شد', 'success');
            } else {
                this.showNotification('تحلیل پیشرفت انجام شد', 'info');
            }
            
        } catch (error) {
            this.rewardLoading.classList.add('hidden');
            this.showNotification(`خطا در تحلیل پیشرفت: ${error.message}`, 'error');
        } finally {
            this.analyzeRewardBtn.disabled = false;
        }
    }

    // Copy reward analysis to clipboard
    copyRewardAnalysisToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('نتیجه تحلیل پاداش کپی شد', 'success');
        }).catch(err => {
            this.showNotification('خطا در کپی کردن', 'error');
        });
    }

    // Share reward analysis
    shareRewardAnalysis(text) {
        if (navigator.share) {
            navigator.share({
                title: 'تحلیل پاداش AriaRobot',
                text: text
            }).catch(err => {
                this.showNotification('خطا در اشتراک‌گذاری', 'error');
            });
        } else {
            // Fallback to copying
            this.copyRewardAnalysisToClipboard(text);
        }
    }

    // List reward logs
    async listRewardLogs() {
        try {
            const response = await fetch('/agent/reward/logs/public');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Display reward logs
            this.rewardResult.classList.remove('hidden');
            
            if (data.rewards && data.rewards.length > 0) {
                let logsHtml = `
                    <div class="space-y-3">
                        <h4 class="font-bold text-lg mb-3">📋 تاریخچه پاداش‌ها (${data.count} مورد)</h4>
                `;
                
                data.rewards.forEach(reward => {
                    const date = new Date(reward.timestamp).toLocaleString('fa-IR');
                    const triggerTypes = {
                        'emotional_recovery': 'بهبود عاطفی',
                        'goal_alignment': 'هماهنگی با اهداف',
                        'security_improvement': 'بهبود امنیت ذهنی',
                        'stress_reduction': 'کاهش استرس',
                        'positive_mindset': 'تفکر مثبت',
                        'breakthrough': 'کشف جدید',
                        'consistency': 'ثبات و پایداری'
                    };
                    
                    const triggerPersian = triggerTypes[reward.trigger_type] || reward.trigger_type;
                    const confidenceBar = '█'.repeat(Math.floor(reward.confidence * 5)) + '░'.repeat(5 - Math.floor(reward.confidence * 5));
                    
                    logsHtml += `
                        <div class="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                            <div class="flex items-start gap-3">
                                <div class="text-2xl">${reward.emoji}</div>
                                <div class="flex-1 space-y-1">
                                    <div class="font-medium text-gray-800">${reward.reward_message}</div>
                                    <div class="text-sm text-gray-600">
                                        🎯 <strong>نوع:</strong> ${triggerPersian} | 
                                        📈 <strong>اطمینان:</strong> ${confidenceBar} (${(reward.confidence * 100).toFixed(1)}%)
                                    </div>
                                    <div class="text-xs text-gray-500">📅 ${date}</div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                logsHtml += `
                    </div>
                    <div class="mt-4 text-center">
                        <button 
                            onclick="clearRewardAnalysis()"
                            class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
                        >
                            🗑️ بستن لیست
                        </button>
                    </div>
                `;
                
                this.rewardContent.innerHTML = logsHtml;
            } else {
                this.rewardContent.innerHTML = `
                    <div class="text-center py-8">
                        <div class="text-6xl mb-4">🏆</div>
                        <div class="text-lg text-gray-600 mb-2">هنوز پاداشی دریافت نکرده‌اید</div>
                        <div class="text-sm text-gray-500">پیشرفت‌های خود را بنویسید تا پاداش دریافت کنید</div>
                    </div>
                `;
            }
            
        } catch (error) {
            this.showNotification(`خطا در دریافت تاریخچه پاداش‌ها: ${error.message}`, 'error');
        }
    }

    // Clear reward analysis
    clearRewardAnalysis() {
        this.rewardInput.value = '';
        this.rewardResult.classList.add('hidden');
        this.rewardContent.innerHTML = '';
        this.showNotification('تحلیل پاداش پاک شد', 'success');
    }

    // Analyze bias
    async analyzeBias() {
        const input = this.biasInput.value.trim();
        if (!input) {
            this.showNotification('لطفاً متن، تصمیم، یا نظر خود را وارد کنید.', 'warning');
            return;
        }

        this.analyzeBiasBtn.disabled = true;
        this.biasLoading.classList.remove('hidden');
        this.biasResult.classList.add('hidden');

        try {
            // Use public endpoint for testing
            const response = await fetch('/agent/bias-detection/analyze/public', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: input,
                    context: {}
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            this.biasLoading.classList.add('hidden');
            this.biasResult.classList.remove('hidden');
            
            // Display bias analysis result
            this.biasContent.innerHTML = `
                <div class="whitespace-pre-wrap font-mono text-sm text-gray-800 rtl">
                    ${data.content}
                </div>
                <div class="mt-3 flex gap-2">
                    <button 
                        onclick="copyBiasAnalysisToClipboard(\`${data.content.replace(/`/g, '\\`')}\`)"
                        class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm"
                    >
                        📋 کپی
                    </button>
                    <button 
                        onclick="shareBiasAnalysis(\`${data.content.replace(/`/g, '\\`')}\`)"
                        class="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm"
                    >
                        🔗 اشتراک
                    </button>
                </div>
            `;
            
            // Show success notification
            this.showNotification('تحلیل سوگیری انجام شد', 'success');
            
        } catch (error) {
            this.biasLoading.classList.add('hidden');
            this.showNotification(`خطا در تحلیل سوگیری: ${error.message}`, 'error');
        } finally {
            this.analyzeBiasBtn.disabled = false;
        }
    }

    // Copy bias analysis to clipboard
    copyBiasAnalysisToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('نتیجه تحلیل سوگیری کپی شد', 'success');
        }).catch(err => {
            this.showNotification('خطا در کپی کردن', 'error');
        });
    }

    // Share bias analysis
    shareBiasAnalysis(text) {
        if (navigator.share) {
            navigator.share({
                title: 'تحلیل سوگیری AriaRobot',
                text: text
            }).catch(err => {
                this.showNotification('خطا در اشتراک‌گذاری', 'error');
            });
        } else {
            // Fallback to copying
            this.copyBiasAnalysisToClipboard(text);
        }
    }

    // List bias logs
    async listBiasLogs() {
        try {
            // Use public endpoint for testing
            const response = await fetch('/agent/bias-detection/logs/public');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Display bias logs
            this.biasResult.classList.remove('hidden');
            
            if (data.bias_logs && data.bias_logs.length > 0) {
                let logsHtml = `
                    <div class="space-y-3">
                        <h4 class="font-bold text-lg mb-3">📋 تاریخچه تحلیل سوگیری (${data.count} مورد)</h4>
                `;
                
                data.bias_logs.forEach(log => {
                    const date = new Date(log.timestamp).toLocaleString('fa-IR');
                    const biasTypes = log.bias_type || [];
                    const biasDisplay = biasTypes.length > 0 ? biasTypes.join(', ') : 'هیچ سوگیری شناسایی نشد';
                    
                    // Create severity bar
                    const severityBar = '█'.repeat(Math.floor(log.severity_score * 5)) + '░'.repeat(5 - Math.floor(log.severity_score * 5));
                    
                    // Choose color based on severity
                    let severityColor = 'bg-green-50 border-green-200';
                    if (log.severity_score >= 0.7) {
                        severityColor = 'bg-red-50 border-red-200';
                    } else if (log.severity_score >= 0.5) {
                        severityColor = 'bg-yellow-50 border-yellow-200';
                    }
                    
                    logsHtml += `
                        <div class="${severityColor} p-3 rounded-lg border">
                            <div class="flex items-start gap-3">
                                <div class="text-2xl">🧠</div>
                                <div class="flex-1 space-y-1">
                                    <div class="text-sm text-gray-600 truncate">${log.input_text}</div>
                                    <div class="font-medium text-gray-800">${biasDisplay}</div>
                                    <div class="text-sm text-gray-600">
                                        📊 <strong>شدت:</strong> ${severityBar} (${(log.severity_score * 100).toFixed(1)}%)
                                    </div>
                                    <div class="text-sm text-blue-600">${log.suggestion}</div>
                                    <div class="text-xs text-gray-500">📅 ${date}</div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                logsHtml += `
                    </div>
                    <div class="mt-4 text-center">
                        <button 
                            onclick="clearBiasAnalysis()"
                            class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
                        >
                            🗑️ بستن لیست
                        </button>
                    </div>
                `;
                
                this.biasContent.innerHTML = logsHtml;
            } else {
                this.biasContent.innerHTML = `
                    <div class="text-center py-8">
                        <div class="text-6xl mb-4">🧠</div>
                        <div class="text-lg text-gray-600 mb-2">هنوز تحلیل سوگیری انجام نشده</div>
                        <div class="text-sm text-gray-500">متن یا تصمیم خود را بنویسید تا تحلیل انجام شود</div>
                    </div>
                `;
            }
            
        } catch (error) {
            this.showNotification(`خطا در دریافت تاریخچه سوگیری: ${error.message}`, 'error');
        }
    }

    // Clear bias analysis
    clearBiasAnalysis() {
        this.biasInput.value = '';
        this.biasResult.classList.add('hidden');
        this.biasContent.innerHTML = '';
        this.showNotification('تحلیل سوگیری پاک شد', 'success');
    }

    // Ethical reasoning analysis
    async analyzeEthical() {
        const text = this.ethicalInput.value.trim();
        
        if (!text) {
            this.showNotification('لطفاً متن یا تصمیم خود را وارد کنید.', 'warning');
            return;
        }
        
        if (text.length < 10) {
            this.showNotification('متن باید حداقل 10 کاراکتر باشد.', 'warning');
            return;
        }
        
        this.ethicalLoading.classList.remove('hidden');
        this.ethicalResult.classList.add('hidden');
        this.analyzeEthicalBtn.disabled = true;
        
        try {
            const response = await fetch(`${this.apiBase}/agent/ethical-reasoning/analyze/public`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                mode: 'cors',
                body: JSON.stringify({ 
                    message: text,
                    context: {}
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.displayEthicalAnalysis(data);
            } else {
                throw new Error(data.error || 'خطا در تحلیل اخلاقی');
            }
            
        } catch (error) {
            console.error('Ethical analysis error:', error);
            this.showNotification(`خطا در تحلیل اخلاقی: ${error.message}`, 'error');
        } finally {
            this.ethicalLoading.classList.add('hidden');
            this.analyzeEthicalBtn.disabled = false;
        }
    }

    // Display ethical analysis result
    displayEthicalAnalysis(data) {
        const response = data.content;
        
        this.ethicalContent.innerHTML = `
            <div class="ethical-analysis">
                <div class="bg-gradient-to-r from-indigo-50 to-purple-50 p-4 rounded-lg">
                    <h4 class="font-semibold text-indigo-800 mb-2">📊 نتیجه تحلیل اخلاقی</h4>
                    <div class="space-y-3">
                        <div class="text-gray-700 leading-relaxed">
                            ${response.replace(/\n/g, '<br>')}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.ethicalResult.classList.remove('hidden');
        this.showNotification('تحلیل اخلاقی با موفقیت انجام شد', 'success');
    }

    // List ethical reasoning logs
    async listEthicalLogs() {
        try {
            const response = await fetch(`${this.apiBase}/agent/ethical-reasoning/logs/public`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                mode: 'cors'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.logs && data.logs.length > 0) {
                let logsHtml = `
                    <div class="space-y-3">
                        <h4 class="font-semibold text-gray-800 mb-3">📋 تاریخچه تحلیل‌های اخلاقی</h4>
                `;
                
                data.logs.forEach(log => {
                    const date = new Date(log.timestamp).toLocaleString('fa-IR');
                    
                    // Parse analysis data if it's a JSON string
                    let frameworkFlags = [];
                    try {
                        frameworkFlags = JSON.parse(log.framework_flags || '[]');
                    } catch (e) {
                        frameworkFlags = [];
                    }
                    
                    // Choose color based on status
                    let statusColor = 'bg-green-50 border-green-200';
                    let statusIcon = '✅';
                    if (log.status === 'alert') {
                        statusColor = 'bg-red-50 border-red-200';
                        statusIcon = '🚨';
                    } else if (log.status === 'warning') {
                        statusColor = 'bg-yellow-50 border-yellow-200';
                        statusIcon = '⚠️';
                    }
                    
                    // Create confidence bar
                    const confidenceBar = '█'.repeat(Math.floor(log.confidence * 5)) + '░'.repeat(5 - Math.floor(log.confidence * 5));
                    
                    logsHtml += `
                        <div class="${statusColor} p-3 rounded-lg border">
                            <div class="flex items-start gap-3">
                                <div class="text-2xl">${statusIcon}</div>
                                <div class="flex-1 space-y-1">
                                    <div class="text-sm text-gray-600 truncate">${log.input_text}</div>
                                    <div class="font-medium text-gray-800">وضعیت: ${log.status}</div>
                                    <div class="text-sm text-gray-600">
                                        📊 <strong>اطمینان:</strong> ${confidenceBar} (${(log.confidence * 100).toFixed(1)}%)
                                    </div>
                                    ${frameworkFlags.length > 0 ? `<div class="text-sm text-purple-600">چارچوب‌های فعال: ${frameworkFlags.join(', ')}</div>` : ''}
                                    <div class="text-sm text-blue-600">${log.guidance}</div>
                                    <div class="text-xs text-gray-500">📅 ${date}</div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                logsHtml += `
                    </div>
                    <div class="mt-4 text-center">
                        <button 
                            onclick="clearEthicalAnalysis()"
                            class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
                        >
                            🗑️ بستن لیست
                        </button>
                    </div>
                `;
                
                this.ethicalContent.innerHTML = logsHtml;
            } else {
                this.ethicalContent.innerHTML = `
                    <div class="text-center py-8">
                        <div class="text-6xl mb-4">🧭</div>
                        <div class="text-lg text-gray-600 mb-2">هنوز تحلیل اخلاقی انجام نشده</div>
                        <div class="text-sm text-gray-500">متن یا تصمیم خود را بنویسید تا تحلیل انجام شود</div>
                    </div>
                `;
            }
            
            this.ethicalResult.classList.remove('hidden');
            
        } catch (error) {
            this.showNotification(`خطا در دریافت تاریخچه اخلاقی: ${error.message}`, 'error');
        }
    }

    // Clear ethical analysis
    clearEthicalAnalysis() {
        this.ethicalInput.value = '';
        this.ethicalResult.classList.add('hidden');
        this.ethicalContent.innerHTML = '';
        this.showNotification('تحلیل اخلاقی پاک شد', 'success');
    }

    // List recent decisions
    async listRecentDecisions() {
        try {
            const response = await fetch(`${this.apiBase}/agent/decision-support/list/public`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                mode: 'cors'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.decisions && data.decisions.length > 0) {
                this.displayDecisionsList(data.decisions);
            } else {
                this.showNotification('هیچ تصمیم قبلی یافت نشد.', 'info');
            }

        } catch (error) {
            console.error('List decisions error:', error);
            this.showNotification(`خطا در دریافت فهرست تصمیمات: ${error.message}`, 'error');
        }
    }

    // Display list of recent decisions
    displayDecisionsList(decisions) {
        const listHTML = `
            <div class="decisions-list">
                <div class="mb-4">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-2xl">📋</span>
                        <h3 class="text-lg font-bold text-gray-800">تصمیمات قبلی (${decisions.length})</h3>
                    </div>
                </div>
                
                <div class="space-y-3 max-h-80 overflow-y-auto">
                    ${decisions.map((decision, index) => `
                        <div class="bg-white p-3 rounded-lg border border-gray-200 hover:border-purple-300 transition-colors">
                            <div class="flex items-start justify-between mb-2">
                                <span class="text-xs text-gray-500">#${decision.id} - ${new Date(decision.created_at).toLocaleDateString('fa-IR')}</span>
                                <span class="risk-badge ${decision.risk_level} px-2 py-1 rounded text-xs">
                                    ${decision.risk_level === 'low' ? '🟢 کم‌خطر' : 
                                      decision.risk_level === 'medium' ? '🟡 متوسط' : '🔴 پرخطر'}
                                </span>
                            </div>
                            <p class="text-sm text-gray-700 mb-2">${decision.decision_text}</p>
                            <div class="text-xs text-gray-600">
                                <span class="mr-3">📈 اعتماد: ${Math.round(decision.confidence_score * 100)}%</span>
                                <span class="mr-3">💝 احساس: ${decision.emotional_state}</span>
                            </div>
                            <div class="text-xs text-purple-600 mt-1">${decision.recommendation}</div>
                        </div>
                    `).join('')}
                </div>
                
                <div class="flex gap-2 mt-4">
                    <button 
                        onclick="clearDecisionAnalysis()"
                        class="bg-purple-500 hover:bg-purple-600 text-white px-3 py-1 rounded text-sm transition-colors duration-200"
                    >
                        🆕 تحلیل جدید
                    </button>
                </div>
            </div>
        `;

        this.decisionContent.innerHTML = listHTML;
        this.decisionResult.classList.remove('hidden');
    }
}

// Global functions for HTML onclick handlers
let ariaRobot;

function sendMessage() {
    ariaRobot.sendMessage();
}

function showMemory() {
    ariaRobot.showMemory();
}

function clearMemory() {
    ariaRobot.clearMemory();
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function analyzeSentiment() {
    ariaRobot.analyzeSentiment();
}

function handleSentimentKeyPress(event) {
    if (event.key === 'Enter') {
        analyzeSentiment();
    }
}

function summarizeText() {
    ariaRobot.summarizeText();
}

function copyToClipboard(text) {
    ariaRobot.copyToClipboard(text);
}

function clearSummaryResult() {
    ariaRobot.clearSummaryResult();
}

function saveMemory() {
    ariaRobot.saveMemory();
}

function fetchMemories() {
    ariaRobot.fetchMemories();
}

function copyMemoryToClipboard(text) {
    ariaRobot.copyMemoryToClipboard(text);
}

function clearMemoryResult() {
    ariaRobot.clearMemoryResult();
}

function analyzeConcept() {
    ariaRobot.analyzeConcept();
}

function fetchLatestConcepts() {
    ariaRobot.fetchLatestConcepts();
}

function copyConceptualToClipboard(text) {
    ariaRobot.copyConceptualToClipboard(text);
}

function clearConceptualResult() {
    ariaRobot.clearConceptualResult();
}

function observeRepetitivePattern() {
    ariaRobot.observeRepetitivePattern();
}

function fetchFrequentPatterns() {
    ariaRobot.fetchFrequentPatterns();
}

function copyRepetitiveToClipboard(text) {
    ariaRobot.copyRepetitiveToClipboard(text);
}

function clearRepetitiveResult() {
    ariaRobot.clearRepetitiveResult();
}

function buildKnowledgeGraph() {
    ariaRobot.buildKnowledgeGraph();
}

function listKnowledgeGraphs() {
    ariaRobot.listKnowledgeGraphs();
}

function copyKnowledgeGraphToClipboard(text) {
    ariaRobot.copyKnowledgeGraphToClipboard(text);
}

function clearKnowledgeGraphResult() {
    ariaRobot.clearKnowledgeGraphResult();
}

function getCompletion() {
    ariaRobot.getCompletion();
}

function getHints() {
    ariaRobot.getHints();
}

function getSmartSuggestions() {
    ariaRobot.getSmartSuggestions();
}

function copySuggesterToClipboard(text) {
    ariaRobot.copySuggesterToClipboard(text);
}

function clearSuggesterResult() {
    ariaRobot.clearSuggesterResult();
}

function analyzeGoal() {
    ariaRobot.analyzeGoal();
}

function copyGoalAnalysisToClipboard(text) {
    ariaRobot.copyGoalAnalysisToClipboard(text);
}

function clearGoalAnalysis() {
    ariaRobot.clearGoalAnalysis();
}

function analyzeEmotion() {
    ariaRobot.analyzeEmotion();
}

function copyEmotionAnalysisToClipboard(text) {
    ariaRobot.copyEmotionAnalysisToClipboard(text);
}

function clearEmotionAnalysis() {
    ariaRobot.clearEmotionAnalysis();
}

function analyzeDecision() {
    ariaRobot.analyzeDecision();
}

function copyDecisionAnalysisToClipboard(text) {
    ariaRobot.copyDecisionAnalysisToClipboard(text);
}

function clearDecisionAnalysis() {
    ariaRobot.clearDecisionAnalysis();
}

function listRecentDecisions() {
    ariaRobot.listRecentDecisions();
}

// Rewards functions
function showRewards() {
    hideAllSections();
    const rewardsSection = document.getElementById('rewardsSection');
    if (rewardsSection) {
        rewardsSection.classList.remove('hidden');
    }
}

function analyzeReward() {
    ariaRobot.analyzeReward();
}

function copyRewardAnalysisToClipboard(text) {
    ariaRobot.copyRewardAnalysisToClipboard(text);
}

function shareRewardAnalysis(text) {
    ariaRobot.shareRewardAnalysis(text);
}

function listRewardLogs() {
    ariaRobot.listRewardLogs();
}

function clearRewardAnalysis() {
    ariaRobot.clearRewardAnalysis();
}

// Bias detection functions
function showBiasDetection() {
    hideAllSections();
    const biasDetectionSection = document.getElementById('biasDetectionSection');
    if (biasDetectionSection) {
        biasDetectionSection.classList.remove('hidden');
    }
}

function analyzeBias() {
    ariaRobot.analyzeBias();
}

function copyBiasAnalysisToClipboard(text) {
    ariaRobot.copyBiasAnalysisToClipboard(text);
}

function shareBiasAnalysis(text) {
    ariaRobot.shareBiasAnalysis(text);
}

function listBiasLogs() {
    ariaRobot.listBiasLogs();
}

function clearBiasAnalysis() {
    ariaRobot.clearBiasAnalysis();
}

// SelfAwareness functions
function showSelfAwareness() {
    hideAllSections();
    const awarenessSection = document.getElementById('selfAwarenessSection');
    if (awarenessSection) {
        awarenessSection.classList.remove('hidden');
    }
}

async function analyzeSelfAwareness() {
    const input = document.getElementById('awarenessInput').value.trim();
    const button = document.getElementById('analyzeAwarenessBtn');
    const result = document.getElementById('awarenessResult');
    const content = document.getElementById('awarenessContent');
    const loading = document.getElementById('awarenessLoading');
    
    if (!input) {
        alert('لطفاً وضعیت ذهنی خود را بیان کنید');
        return;
    }
    
    // Show loading
    loading.classList.remove('hidden');
    result.classList.add('hidden');
    button.disabled = true;
    
    try {
        const response = await fetch('/agent/self-awareness/analyze/public', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: input,
                context: {}
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            content.innerHTML = formatSelfAwarenessResponse(data.content);
            result.classList.remove('hidden');
        } else {
            content.innerHTML = `<div class="text-red-600">خطا: ${data.content}</div>`;
            result.classList.remove('hidden');
        }
        
    } catch (error) {
        console.error('Error analyzing self-awareness:', error);
        content.innerHTML = `<div class="text-red-600">خطا در اتصال به سرور</div>`;
        result.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
        button.disabled = false;
    }
}

function formatSelfAwarenessResponse(content) {
    // Parse JSON if it's structured data
    try {
        const data = JSON.parse(content);
        return `
            <div class="space-y-4">
                <div class="border-l-4 border-purple-500 pl-4">
                    <h4 class="font-medium text-purple-800 mb-2">تحلیل خودآگاهی</h4>
                    <div class="text-gray-700">${data.analysis || content}</div>
                </div>
                ${data.status ? `
                <div class="flex items-center gap-2">
                    <span class="text-sm font-medium">وضعیت:</span>
                    <span class="px-2 py-1 rounded text-sm ${getStatusColor(data.status)}">${data.status}</span>
                </div>
                ` : ''}
                ${data.confidence ? `
                <div class="flex items-center gap-2">
                    <span class="text-sm font-medium">اطمینان:</span>
                    <span class="text-sm">${Math.round(data.confidence * 100)}%</span>
                </div>
                ` : ''}
                ${data.alert ? `
                <div class="border-l-4 border-yellow-500 pl-4 bg-yellow-50 p-3 rounded">
                    <p class="text-yellow-800">${data.alert}</p>
                </div>
                ` : ''}
            </div>
        `;
    } catch (e) {
        // If not JSON, return as plain text with formatting
        return `
            <div class="prose prose-sm max-w-none text-right">
                ${content.replace(/\n/g, '<br>')}
            </div>
        `;
    }
}

function getStatusColor(status) {
    switch (status) {
        case 'ok': return 'bg-green-100 text-green-800';
        case 'warning': return 'bg-yellow-100 text-yellow-800';
        case 'alert': return 'bg-red-100 text-red-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}

function clearAwarenessAnalysis() {
    document.getElementById('awarenessInput').value = '';
    document.getElementById('awarenessResult').classList.add('hidden');
}

async function listAwarenessLogs() {
    const button = document.getElementById('listAwarenessLogsBtn');
    const result = document.getElementById('awarenessResult');
    const content = document.getElementById('awarenessContent');
    const loading = document.getElementById('awarenessLoading');
    
    // Show loading
    loading.classList.remove('hidden');
    result.classList.add('hidden');
    button.disabled = true;
    
    try {
        const response = await fetch('/agent/self-awareness/logs/public', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.logs && data.logs.length > 0) {
            content.innerHTML = formatAwarenessLogs(data.logs);
            result.classList.remove('hidden');
        } else {
            content.innerHTML = '<div class="text-gray-600">هیچ گزارش خودآگاهی یافت نشد</div>';
            result.classList.remove('hidden');
        }
        
    } catch (error) {
        console.error('Error fetching awareness logs:', error);
        content.innerHTML = `<div class="text-red-600">خطا در دریافت گزارش‌ها</div>`;
        result.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
        button.disabled = false;
    }
}

function formatAwarenessLogs(logs) {
    return `
        <div class="space-y-4">
            <h4 class="font-medium text-purple-800 mb-4">گزارش‌های اخیر تحلیل خودآگاهی (${logs.length} مورد)</h4>
            ${logs.map(log => `
                <div class="border border-purple-200 rounded-lg p-4 bg-purple-50">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-sm text-gray-600">${new Date(log.created_at).toLocaleDateString('fa-IR')}</span>
                        <span class="px-2 py-1 rounded text-xs ${getStatusColor(log.status)}">${log.status}</span>
                    </div>
                    <div class="text-sm text-gray-700 mb-2">
                        <strong>متن:</strong> ${log.input_text.substring(0, 100)}${log.input_text.length > 100 ? '...' : ''}
                    </div>
                    <div class="text-sm text-gray-700 mb-2">
                        <strong>تحلیل:</strong> ${log.alert}
                    </div>
                    <div class="text-xs text-gray-500">
                        اطمینان: ${Math.round(log.confidence * 100)}%
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Security Check Functions
function showSecurityCheck() {
    hideAllSections();
    document.getElementById('securityCheckSection').classList.remove('hidden');
}

async function analyzeSecurityCheck() {
    const input = document.getElementById('securityInput').value.trim();
    
    if (!input) {
        alert('لطفاً متنی برای بررسی امنیت وارد کنید');
        return;
    }
    
    // Show loading
    document.getElementById('securityLoading').classList.remove('hidden');
    document.getElementById('securityResult').classList.add('hidden');
    
    try {
        const response = await fetch('/agent/security-check/analyze/public', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: input
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySecurityResult(data.content);
        } else {
            throw new Error(data.error || 'خطا در بررسی امنیت');
        }
        
    } catch (error) {
        console.error('Security check error:', error);
        document.getElementById('securityContent').innerHTML = `
            <div class="text-red-600">
                خطا در بررسی امنیت: ${error.message}
            </div>
        `;
        document.getElementById('securityResult').classList.remove('hidden');
    } finally {
        document.getElementById('securityLoading').classList.add('hidden');
    }
}

function displaySecurityResult(content) {
    // Parse JSON data from response if it contains JSON
    let analysisData = {};
    const jsonMatch = content.match(/```json\n([\s\S]*?)\n```/);
    if (jsonMatch) {
        try {
            analysisData = JSON.parse(jsonMatch[1]);
        } catch (e) {
            console.error('Error parsing JSON:', e);
        }
    }

    // Extract alert level color
    const alertColor = {
        'green': 'bg-green-100 border-green-300 text-green-800',
        'yellow': 'bg-yellow-100 border-yellow-300 text-yellow-800',
        'red': 'bg-red-100 border-red-300 text-red-800'
    };

    const alertEmoji = {
        'green': '🟢',
        'yellow': '🟡',
        'red': '🔴'
    };

    const alertLevel = analysisData.alert_level || 'green';
    
    const formattedContent = `
        <div class="security-analysis-result">
            <div class="mb-4 p-4 rounded-lg ${alertColor[alertLevel] || alertColor['green']}">
                <div class="flex items-center gap-2 mb-2">
                    <span class="text-2xl">${alertEmoji[alertLevel] || '🟢'}</span>
                    <h4 class="font-bold">نتیجه بررسی امنیت ذهنی</h4>
                </div>
                <div class="text-sm">
                    <strong>سطح هشدار:</strong> ${alertLevel}
                    ${analysisData.risk_score ? `| <strong>امتیاز خطر:</strong> ${(analysisData.risk_score * 100).toFixed(1)}%` : ''}
                </div>
            </div>
            
            <div class="prose max-w-none">
                ${formatMarkdownContent(content)}
            </div>
        </div>
    `;
    
    document.getElementById('securityContent').innerHTML = formattedContent;
    document.getElementById('securityResult').classList.remove('hidden');
}

async function listSecurityChecks() {
    try {
        document.getElementById('securityLoading').classList.remove('hidden');
        
        const response = await fetch('/agent/security-check/list/public');
        const data = await response.json();
        
        if (data.security_checks) {
            const formattedLogs = formatSecurityChecks(data.security_checks);
            document.getElementById('securityContent').innerHTML = formattedLogs;
            document.getElementById('securityResult').classList.remove('hidden');
        } else {
            throw new Error(data.error || 'خطا در دریافت گزارش‌ها');
        }
        
    } catch (error) {
        console.error('List security checks error:', error);
        document.getElementById('securityContent').innerHTML = `
            <div class="text-red-600">
                خطا در دریافت گزارش‌های امنیت: ${error.message}
            </div>
        `;
        document.getElementById('securityResult').classList.remove('hidden');
    } finally {
        document.getElementById('securityLoading').classList.add('hidden');
    }
}

function formatSecurityChecks(checks) {
    const alertColor = {
        'green': 'bg-green-100 text-green-800',
        'yellow': 'bg-yellow-100 text-yellow-800',
        'red': 'bg-red-100 text-red-800'
    };

    const alertEmoji = {
        'green': '🟢',
        'yellow': '🟡',
        'red': '🔴'
    };

    return `
        <div class="space-y-4">
            <h4 class="font-medium text-red-800 mb-4">گزارش‌های اخیر بررسی امنیت (${checks.length} مورد)</h4>
            ${checks.map(check => `
                <div class="border border-red-200 rounded-lg p-4 bg-red-50">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-sm text-gray-600">${new Date(check.created_at).toLocaleDateString('fa-IR')}</span>
                        <span class="px-2 py-1 rounded text-xs flex items-center gap-1 ${alertColor[check.alert_level] || alertColor['green']}">
                            ${alertEmoji[check.alert_level] || '🟢'} ${check.alert_level}
                        </span>
                    </div>
                    <div class="text-sm text-gray-700 mb-2">
                        <strong>متن:</strong> ${check.input_text.substring(0, 100)}${check.input_text.length > 100 ? '...' : ''}
                    </div>
                    <div class="text-sm text-gray-700 mb-2">
                        <strong>نوع تهدید:</strong> ${check.detected_threat_type}
                    </div>
                    <div class="text-sm text-gray-700 mb-2">
                        <strong>توصیه:</strong> ${check.recommendation}
                    </div>
                    <div class="text-xs text-gray-500">
                        امتیاز خطر: ${Math.round(check.risk_score * 100)}%
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function clearSecurityAnalysis() {
    document.getElementById('securityInput').value = '';
    document.getElementById('securityResult').classList.add('hidden');
    document.getElementById('securityLoading').classList.add('hidden');
}

// CognitiveDistortionAgent functions
function showCognitiveDistortion() {
    hideAllSections();
    document.getElementById('cognitiveDistortionSection').classList.remove('hidden');
    document.getElementById('distortionInput').focus();
}

async function analyzeDistortion() {
    const input = document.getElementById('distortionInput').value.trim();
    if (!input) {
        alert('لطفاً متن خود را برای تحلیل تحریف‌های شناختی وارد کنید');
        return;
    }
    
    const loading = document.getElementById('distortionLoading');
    const result = document.getElementById('distortionResult');
    const content = document.getElementById('distortionContent');
    const button = document.getElementById('analyzeDistortionBtn');
    
    loading.classList.remove('hidden');
    result.classList.add('hidden');
    button.disabled = true;
    
    try {
        const response = await fetch('/agent/cognitive-distortion/analyze/public', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: input })
        });
        
        const data = await response.json();
        
        if (data.success) {
            content.innerHTML = `
                <div class="prose prose-sm max-w-none text-right">
                    ${data.content.replace(/\n/g, '<br>')}
                </div>
                <div class="mt-4 flex gap-2">
                    <button onclick="copyDistortionAnalysisToClipboard('${data.content.replace(/'/g, "\\'")}');" 
                            class="bg-pink-500 hover:bg-pink-600 text-white px-3 py-1 rounded text-sm">
                        📋 کپی
                    </button>
                    <button onclick="shareDistortionAnalysis('${data.content.replace(/'/g, "\\'")}');" 
                            class="bg-purple-500 hover:bg-purple-600 text-white px-3 py-1 rounded text-sm">
                        🔗 اشتراک
                    </button>
                </div>
            `;
            result.classList.remove('hidden');
        } else {
            content.innerHTML = `<div class="text-red-600">خطا: ${data.content}</div>`;
            result.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Distortion analysis error:', error);
        content.innerHTML = `<div class="text-red-600">خطا در تحلیل: ${error.message}</div>`;
        result.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
        button.disabled = false;
    }
}

function clearDistortionAnalysis() {
    document.getElementById('distortionInput').value = '';
    document.getElementById('distortionResult').classList.add('hidden');
    document.getElementById('distortionContent').innerHTML = '';
    document.getElementById('distortionInput').focus();
}

async function listDistortionLogs() {
    const loading = document.getElementById('distortionLoading');
    const result = document.getElementById('distortionResult');
    const content = document.getElementById('distortionContent');
    
    loading.classList.remove('hidden');
    result.classList.add('hidden');
    
    try {
        const response = await fetch('/agent/cognitive-distortion/logs/public');
        const data = await response.json();
        
        if (data.distortion_logs && data.distortion_logs.length > 0) {
            let logsHtml = `
                <div class="space-y-3">
                    <h4 class="font-bold text-lg mb-3">📋 تاریخچه تحلیل تحریف‌های شناختی (${data.count} مورد)</h4>
            `;
            
            data.distortion_logs.forEach(log => {
                const date = new Date(log.timestamp).toLocaleString('fa-IR');
                const distortionTypes = log.detected_types || [];
                const distortionDisplay = distortionTypes.length > 0 ? distortionTypes.join(', ') : 'هیچ تحریف شناختی شناسایی نشد';
                
                // Create severity bar
                const severityBar = '█'.repeat(Math.floor(log.severity_score * 5)) + '░'.repeat(5 - Math.floor(log.severity_score * 5));
                
                // Choose color based on severity
                let severityColor = 'bg-green-50 border-green-200';
                if (log.severity_score >= 0.7) {
                    severityColor = 'bg-red-50 border-red-200';
                } else if (log.severity_score >= 0.5) {
                    severityColor = 'bg-yellow-50 border-yellow-200';
                }
                
                logsHtml += `
                    <div class="${severityColor} p-3 rounded-lg border">
                        <div class="flex items-start gap-3">
                            <div class="text-2xl">🧠</div>
                            <div class="flex-1 space-y-1">
                                <div class="text-sm text-gray-600 truncate">${log.input_text}</div>
                                <div class="font-medium text-gray-800">${distortionDisplay}</div>
                                <div class="text-sm text-gray-600">
                                    📊 <strong>شدت:</strong> ${severityBar} (${(log.severity_score * 100).toFixed(1)}%)
                                </div>
                                <div class="text-sm text-purple-600">${log.recommendation}</div>
                                <div class="text-xs text-gray-500">📅 ${date}</div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            logsHtml += `
                </div>
                <div class="mt-4 text-center">
                    <button onclick="clearDistortionAnalysis();" 
                            class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded">
                        🗑️ بستن لیست
                    </button>
                </div>
            `;
            
            content.innerHTML = logsHtml;
        } else {
            content.innerHTML = `
                <div class="text-center py-8">
                    <div class="text-6xl mb-4">🧠</div>
                    <div class="text-lg text-gray-600 mb-2">هنوز تحلیل تحریف‌های شناختی انجام نشده</div>
                    <div class="text-sm text-gray-500">افکار و احساسات خود را بنویسید تا تحلیل انجام شود</div>
                </div>
            `;
        }
        
        result.classList.remove('hidden');
    } catch (error) {
        console.error('List distortion logs error:', error);
        content.innerHTML = `<div class="text-red-600">خطا در دریافت تاریخچه: ${error.message}</div>`;
        result.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
    }
}

function showDistortionTypes() {
    const guide = document.getElementById('distortionTypesGuide');
    guide.classList.toggle('hidden');
}

function copyDistortionAnalysisToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('نتیجه تحلیل تحریف‌ها کپی شد!');
    }).catch(err => {
        console.error('Copy failed:', err);
        alert('خطا در کپی کردن');
    });
}

function shareDistortionAnalysis(text) {
    if (navigator.share) {
        navigator.share({
            title: 'تحلیل تحریف‌های شناختی AriaRobot',
            text: text
        }).catch(err => {
            console.error('Share failed:', err);
            copyDistortionAnalysisToClipboard(text);
        });
    } else {
        copyDistortionAnalysisToClipboard(text);
    }
}

// Ethical reasoning functions
function showEthicalReasoning() {
    hideAllSections();
    document.getElementById('ethicalReasoningSection').classList.remove('hidden');
}

function analyzeEthical() {
    ariaRobot.analyzeEthical();
}

function listEthicalLogs() {
    ariaRobot.listEthicalLogs();
}

function clearEthicalAnalysis() {
    ariaRobot.clearEthicalAnalysis();
}

function copyEthicalAnalysisToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        ariaRobot.showNotification('تحلیل اخلاقی کپی شد', 'success');
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        ariaRobot.showNotification('خطا در کپی کردن', 'error');
    });
}

function shareEthicalAnalysis(text) {
    if (navigator.share) {
        navigator.share({
            title: 'تحلیل اخلاقی AriaRobot',
            text: text
        }).catch(err => {
            console.error('Share failed:', err);
            copyEthicalAnalysisToClipboard(text);
        });
    } else {
        copyEthicalAnalysisToClipboard(text);
    }
}

// Simulated Consensus Functions
function showSimulatedConsensus() {
    hideAllSections();
    document.getElementById('simulatedConsensusSection').classList.remove('hidden');
}

async function simulateConsensus() {
    const input = document.getElementById('consensusInput').value.trim();
    
    if (!input) {
        alert('لطفاً تصمیم یا معضلی را برای بررسی گروهی وارد کنید.');
        return;
    }
    
    // Show loading
    document.getElementById('consensusLoading').classList.remove('hidden');
    document.getElementById('consensusResult').classList.add('hidden');
    
    // Disable button
    const btn = document.getElementById('simulateConsensusBtn');
    btn.disabled = true;
    btn.innerHTML = '<span>🔄</span><span>در حال پردازش...</span>';
    
    try {
        const response = await fetch('/agent/consensus/simulate/public', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: input,
                context: {}
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('consensusContent').innerHTML = formatConsensusResult(data.content);
            document.getElementById('consensusResult').classList.remove('hidden');
        } else {
            document.getElementById('consensusContent').innerHTML = `<div class="text-red-600">خطا: ${data.error || 'خطا در شبیه‌سازی تصمیم‌گیری گروهی'}</div>`;
            document.getElementById('consensusResult').classList.remove('hidden');
        }
        
    } catch (error) {
        console.error('Error in consensus simulation:', error);
        document.getElementById('consensusContent').innerHTML = `<div class="text-red-600">خطا در اتصال به سرور: ${error.message}</div>`;
        document.getElementById('consensusResult').classList.remove('hidden');
    } finally {
        // Hide loading
        document.getElementById('consensusLoading').classList.add('hidden');
        
        // Re-enable button
        btn.disabled = false;
        btn.innerHTML = '<span>🤝</span><span>شبیه‌سازی تصمیم‌گیری گروهی</span>';
    }
}

function formatConsensusResult(content) {
    // Convert markdown-style formatting to HTML
    let formatted = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/### (.*)/g, '<h4 class="text-lg font-semibold mt-4 mb-2 text-gray-800">$1</h4>')
        .replace(/## (.*)/g, '<h3 class="text-xl font-semibold mt-4 mb-2 text-gray-800">$1</h3>')
        .replace(/# (.*)/g, '<h2 class="text-2xl font-semibold mt-4 mb-2 text-gray-800">$1</h2>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
    
    // Add styling for special elements
    formatted = formatted
        .replace(/🤝/g, '<span class="text-green-600">🤝</span>')
        .replace(/👤/g, '<span class="text-blue-600">👤</span>')
        .replace(/💭/g, '<span class="text-purple-600">💭</span>')
        .replace(/📊/g, '<span class="text-orange-600">📊</span>')
        .replace(/💡/g, '<span class="text-yellow-600">💡</span>')
        .replace(/🎯/g, '<span class="text-red-600">🎯</span>');
    
    return `<div class="space-y-2">${formatted}</div>`;
}

async function listConsensusLogs() {
    try {
        const response = await fetch('/agent/consensus/logs/public');
        const data = await response.json();
        
        if (data.consensus_logs && data.consensus_logs.length > 0) {
            let logsHtml = '<h4 class="font-semibold mb-3 text-gray-800">تاریخچه تصمیمات گروهی:</h4>';
            logsHtml += '<div class="space-y-3">';
            
            data.consensus_logs.forEach(log => {
                const timestamp = new Date(log.timestamp).toLocaleString('fa-IR');
                const confidence = Math.round(log.confidence_score * 100);
                
                logsHtml += `
                    <div class="bg-gray-50 p-3 rounded-lg border-r-4 border-green-500">
                        <div class="flex justify-between items-start mb-2">
                            <span class="text-sm text-gray-500">${timestamp}</span>
                            <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                                اطمینان: ${confidence}%
                            </span>
                        </div>
                        <div class="text-sm text-gray-700 mb-2">
                            <strong>تصمیم:</strong> ${log.input_text}
                        </div>
                        <div class="text-sm text-gray-600">
                            <strong>نتیجه:</strong> ${log.consensus_result.substring(0, 100)}...
                        </div>
                        <div class="text-xs text-gray-500 mt-2">
                            <strong>عامل اصلی:</strong> ${log.primary_contributor}
                        </div>
                    </div>
                `;
            });
            
            logsHtml += '</div>';
            
            document.getElementById('consensusContent').innerHTML = logsHtml;
            document.getElementById('consensusResult').classList.remove('hidden');
        } else {
            document.getElementById('consensusContent').innerHTML = '<div class="text-gray-500">هیچ تصمیم گروهی‌ای یافت نشد.</div>';
            document.getElementById('consensusResult').classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error fetching consensus logs:', error);
        document.getElementById('consensusContent').innerHTML = `<div class="text-red-600">خطا در دریافت تاریخچه: ${error.message}</div>`;
        document.getElementById('consensusResult').classList.remove('hidden');
    }
}

function clearConsensusAnalysis() {
    document.getElementById('consensusInput').value = '';
    document.getElementById('consensusResult').classList.add('hidden');
    document.getElementById('consensusLoading').classList.add('hidden');
}

// ===================== Advanced Memory Manager Functions =====================

function showAdvancedMemoryManager() {
    hideAllSections();
    document.getElementById('advancedMemoryManagerSection').classList.remove('hidden');
    showMemoryAnalyze(); // Show analyze section by default
}

function showMemoryAnalyze() {
    // Hide all memory subsections
    document.getElementById('memoryAnalyzeSection').classList.remove('hidden');
    document.getElementById('memoryRetrieveSection').classList.add('hidden');
    document.getElementById('memorySummarizeSection').classList.add('hidden');
    document.getElementById('memoryStatsSection').classList.add('hidden');
    
    // Update button states
    updateMemoryButtonStates('memoryAnalyzeBtn');
}

function showMemoryRetrieve() {
    // Hide all memory subsections
    document.getElementById('memoryAnalyzeSection').classList.add('hidden');
    document.getElementById('memoryRetrieveSection').classList.remove('hidden');
    document.getElementById('memorySummarizeSection').classList.add('hidden');
    document.getElementById('memoryStatsSection').classList.add('hidden');
    
    // Update button states
    updateMemoryButtonStates('memoryRetrieveBtn');
}

function showMemorySummarize() {
    // Hide all memory subsections
    document.getElementById('memoryAnalyzeSection').classList.add('hidden');
    document.getElementById('memoryRetrieveSection').classList.add('hidden');
    document.getElementById('memorySummarizeSection').classList.remove('hidden');
    document.getElementById('memoryStatsSection').classList.add('hidden');
    
    // Update button states
    updateMemoryButtonStates('memorySummarizeBtn');
}

function showMemoryStats() {
    // Hide all memory subsections
    document.getElementById('memoryAnalyzeSection').classList.add('hidden');
    document.getElementById('memoryRetrieveSection').classList.add('hidden');
    document.getElementById('memorySummarizeSection').classList.add('hidden');
    document.getElementById('memoryStatsSection').classList.remove('hidden');
    
    // Update button states
    updateMemoryButtonStates('memoryStatsBtn');
}

function updateMemoryButtonStates(activeId) {
    const buttons = ['memoryAnalyzeBtn', 'memoryRetrieveBtn', 'memorySummarizeBtn', 'memoryStatsBtn'];
    buttons.forEach(id => {
        const btn = document.getElementById(id);
        if (id === activeId) {
            btn.classList.add('ring-2', 'ring-blue-300');
        } else {
            btn.classList.remove('ring-2', 'ring-blue-300');
        }
    });
}

async function analyzeMemory() {
    const input = document.getElementById('memoryAnalyzeInput').value.trim();
    if (!input) {
        alert('لطفاً محتوای حافظه را وارد کنید');
        return;
    }
    
    const memoryType = document.getElementById('memoryTypeSelect').value;
    const missionId = document.getElementById('missionIdInput').value.trim();
    
    // Show loading
    document.getElementById('memoryLoading').classList.remove('hidden');
    document.getElementById('memoryResult').classList.add('hidden');
    
    try {
        const memoryEntry = {
            content: input,
            metadata: {
                source: 'ui',
                timestamp: new Date().toISOString()
            }
        };
        
        if (memoryType) {
            memoryEntry.memory_type = memoryType;
        }
        
        if (missionId) {
            memoryEntry.mission_id = missionId;
        }
        
        const response = await fetch('/agent/memory/analyze/public', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(memoryEntry)
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        const analysis = data.memory_analysis;
        let resultHtml = '<div class="space-y-4">';
        
        if (analysis.status === 'success') {
            resultHtml += `
                <div class="bg-green-50 p-4 rounded-lg border-l-4 border-green-500">
                    <h5 class="font-medium text-green-800 mb-2">✅ تحلیل موفق</h5>
                    <div class="text-sm text-green-700">
                        <p><strong>نوع حافظه:</strong> ${analysis.memory_type}</p>
                        <p><strong>درجه اهمیت:</strong> ${analysis.importance_score}/10</p>
                        <p><strong>شناسه حافظه:</strong> ${analysis.memory_id}</p>
                        ${analysis.mission_id ? `<p><strong>شناسه ماموریت:</strong> ${analysis.mission_id}</p>` : ''}
                    </div>
                </div>
            `;
        } else {
            resultHtml += `
                <div class="bg-red-50 p-4 rounded-lg border-l-4 border-red-500">
                    <h5 class="font-medium text-red-800 mb-2">❌ خطا در تحلیل</h5>
                    <div class="text-sm text-red-700">
                        <p>${analysis.error || 'خطای نامشخص'}</p>
                    </div>
                </div>
            `;
        }
        
        resultHtml += '</div>';
        
        document.getElementById('memoryContent').innerHTML = resultHtml;
        document.getElementById('memoryResult').classList.remove('hidden');
        
    } catch (error) {
        console.error('Error analyzing memory:', error);
        document.getElementById('memoryContent').innerHTML = `
            <div class="bg-red-50 p-4 rounded-lg border-l-4 border-red-500">
                <h5 class="font-medium text-red-800 mb-2">❌ خطا در ارتباط</h5>
                <div class="text-sm text-red-700">
                    <p>${error.message}</p>
                </div>
            </div>
        `;
        document.getElementById('memoryResult').classList.remove('hidden');
    }
    
    // Hide loading
    document.getElementById('memoryLoading').classList.add('hidden');
}

async function retrieveMemory() {
    const memoryType = document.getElementById('retrieveTypeSelect').value;
    const minImportance = document.getElementById('minImportanceInput').value;
    
    // Show loading
    document.getElementById('memoryLoading').classList.remove('hidden');
    document.getElementById('memoryResult').classList.add('hidden');
    
    try {
        const response = await fetch(`/agent/memory/retrieve/${memoryType}/public?min_importance=${minImportance}&limit=20`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        let resultHtml = '<div class="space-y-4">';
        
        if (data.memories && data.memories.length > 0) {
            resultHtml += `
                <div class="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
                    <h5 class="font-medium text-blue-800 mb-2">📚 حافظه‌های بازیابی شده</h5>
                    <div class="text-sm text-blue-700">
                        <p><strong>تعداد:</strong> ${data.count}</p>
                        <p><strong>نوع:</strong> ${data.memory_type}</p>
                    </div>
                </div>
            `;
            
            data.memories.forEach((memory, index) => {
                const timestamp = new Date(memory.created_at).toLocaleString('fa-IR');
                resultHtml += `
                    <div class="bg-gray-50 p-4 rounded-lg border">
                        <div class="flex justify-between items-start mb-2">
                            <span class="text-xs text-gray-500">حافظه ${index + 1}</span>
                            <div class="flex gap-2">
                                <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                                    اهمیت: ${memory.importance_score}/10
                                </span>
                                <span class="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded-full">
                                    ${timestamp}
                                </span>
                            </div>
                        </div>
                        <div class="text-sm text-gray-700 mb-2">
                            ${memory.content}
                        </div>
                        ${memory.mission_id ? `<div class="text-xs text-gray-500">ماموریت: ${memory.mission_id}</div>` : ''}
                    </div>
                `;
            });
        } else {
            resultHtml += `
                <div class="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-500">
                    <h5 class="font-medium text-yellow-800 mb-2">⚠️ حافظه‌ای یافت نشد</h5>
                    <div class="text-sm text-yellow-700">
                        <p>با معیارهای انتخاب شده، حافظه‌ای در دسترس نیست.</p>
                    </div>
                </div>
            `;
        }
        
        resultHtml += '</div>';
        
        document.getElementById('memoryContent').innerHTML = resultHtml;
        document.getElementById('memoryResult').classList.remove('hidden');
        
    } catch (error) {
        console.error('Error retrieving memory:', error);
        document.getElementById('memoryContent').innerHTML = `
            <div class="bg-red-50 p-4 rounded-lg border-l-4 border-red-500">
                <h5 class="font-medium text-red-800 mb-2">❌ خطا در بازیابی</h5>
                <div class="text-sm text-red-700">
                    <p>${error.message}</p>
                </div>
            </div>
        `;
        document.getElementById('memoryResult').classList.remove('hidden');
    }
    
    // Hide loading
    document.getElementById('memoryLoading').classList.add('hidden');
}

async function summarizeMemory() {
    const memoryType = document.getElementById('summarizeTypeSelect').value;
    const forceRefresh = document.getElementById('forceRefreshCheck').checked;
    
    // Show loading
    document.getElementById('memoryLoading').classList.remove('hidden');
    document.getElementById('memoryResult').classList.add('hidden');
    
    try {
        const response = await fetch(`/agent/memory/summarize/${memoryType}/public?force_refresh=${forceRefresh}`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        const summary = data.summary_data;
        let resultHtml = '<div class="space-y-4">';
        
        if (summary.summary) {
            resultHtml += `
                <div class="bg-purple-50 p-4 rounded-lg border-l-4 border-purple-500">
                    <h5 class="font-medium text-purple-800 mb-2">📄 خلاصه حافظه</h5>
                    <div class="text-sm text-purple-700">
                        <p><strong>نوع:</strong> ${data.memory_type}</p>
                        <p><strong>تعداد ورودی:</strong> ${summary.entry_count}</p>
                        ${summary.last_updated ? `<p><strong>آخرین بروزرسانی:</strong> ${new Date(summary.last_updated).toLocaleString('fa-IR')}</p>` : ''}
                    </div>
                </div>
            `;
            
            resultHtml += `
                <div class="bg-white p-4 rounded-lg border">
                    <div class="text-sm text-gray-700">
                        ${summary.summary}
                    </div>
                </div>
            `;
        } else {
            resultHtml += `
                <div class="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-500">
                    <h5 class="font-medium text-yellow-800 mb-2">⚠️ خلاصه‌ای موجود نیست</h5>
                    <div class="text-sm text-yellow-700">
                        <p>برای این نوع حافظه، اطلاعات کافی برای خلاصه‌سازی وجود ندارد.</p>
                    </div>
                </div>
            `;
        }
        
        resultHtml += '</div>';
        
        document.getElementById('memoryContent').innerHTML = resultHtml;
        document.getElementById('memoryResult').classList.remove('hidden');
        
    } catch (error) {
        console.error('Error summarizing memory:', error);
        document.getElementById('memoryContent').innerHTML = `
            <div class="bg-red-50 p-4 rounded-lg border-l-4 border-red-500">
                <h5 class="font-medium text-red-800 mb-2">❌ خطا در خلاصه‌سازی</h5>
                <div class="text-sm text-red-700">
                    <p>${error.message}</p>
                </div>
            </div>
        `;
        document.getElementById('memoryResult').classList.remove('hidden');
    }
    
    // Hide loading
    document.getElementById('memoryLoading').classList.add('hidden');
}

async function getMemoryStats() {
    // Show loading
    document.getElementById('memoryLoading').classList.remove('hidden');
    document.getElementById('memoryResult').classList.add('hidden');
    
    try {
        const response = await fetch('/agent/memory/statistics/public');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        const stats = data.statistics;
        let resultHtml = '<div class="space-y-4">';
        
        if (stats.total_entries !== undefined) {
            resultHtml += `
                <div class="bg-orange-50 p-4 rounded-lg border-l-4 border-orange-500">
                    <h5 class="font-medium text-orange-800 mb-2">📊 آمار کلی حافظه</h5>
                    <div class="text-sm text-orange-700">
                        <p><strong>تعداد کل:</strong> ${stats.total_entries}</p>
                        <p><strong>تعداد فعال:</strong> ${stats.active_entries}</p>
                        <p><strong>میانگین اهمیت:</strong> ${stats.average_importance ? stats.average_importance.toFixed(1) : 'نامشخص'}</p>
                    </div>
                </div>
            `;
            
            // Memory type breakdown
            if (stats.by_type && Object.keys(stats.by_type).length > 0) {
                resultHtml += `
                    <div class="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
                        <h5 class="font-medium text-blue-800 mb-2">📋 تفکیک بر اساس نوع</h5>
                        <div class="text-sm text-blue-700 space-y-1">
                `;
                
                Object.entries(stats.by_type).forEach(([type, count]) => {
                    const typeNames = {
                        'short_term': 'کوتاه‌مدت',
                        'long_term': 'بلندمدت',
                        'mission_specific': 'ماموریت خاص',
                        'reflective': 'بازتابی'
                    };
                    resultHtml += `<p><strong>${typeNames[type] || type}:</strong> ${count}</p>`;
                });
                
                resultHtml += `
                        </div>
                    </div>
                `;
            }
            
            // Recent activity
            if (stats.recent_activity) {
                resultHtml += `
                    <div class="bg-green-50 p-4 rounded-lg border-l-4 border-green-500">
                        <h5 class="font-medium text-green-800 mb-2">⏱️ فعالیت اخیر</h5>
                        <div class="text-sm text-green-700">
                            <p><strong>امروز:</strong> ${stats.recent_activity.today || 0}</p>
                            <p><strong>هفته گذشته:</strong> ${stats.recent_activity.week || 0}</p>
                            <p><strong>ماه گذشته:</strong> ${stats.recent_activity.month || 0}</p>
                        </div>
                    </div>
                `;
            }
        } else {
            resultHtml += `
                <div class="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-500">
                    <h5 class="font-medium text-yellow-800 mb-2">⚠️ آماری موجود نیست</h5>
                    <div class="text-sm text-yellow-700">
                        <p>در حال حاضر آماری از حافظه در دسترس نیست.</p>
                    </div>
                </div>
            `;
        }
        
        resultHtml += '</div>';
        
        document.getElementById('memoryContent').innerHTML = resultHtml;
        document.getElementById('memoryResult').classList.remove('hidden');
        
    } catch (error) {
        console.error('Error getting memory statistics:', error);
        document.getElementById('memoryContent').innerHTML = `
            <div class="bg-red-50 p-4 rounded-lg border-l-4 border-red-500">
                <h5 class="font-medium text-red-800 mb-2">❌ خطا در دریافت آمار</h5>
                <div class="text-sm text-red-700">
                    <p>${error.message}</p>
                </div>
            </div>
        `;
        document.getElementById('memoryResult').classList.remove('hidden');
    }
    
    // Hide loading
    document.getElementById('memoryLoading').classList.add('hidden');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    ariaRobot = new AriaRobotClient();
    console.log('AriaRobot Client initialized');
});