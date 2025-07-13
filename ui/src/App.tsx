import { useEffect, useState } from "react";
import { AgentPanel } from "./components/agent-panel";
import { Chat } from "./components/Chat";
import { DevPanel } from "./components/dev-panel";
import type { Agent, AgentEvent, GuardrailCheck, Message } from "./lib/types";
import { callChatAPI } from "./lib/api";
import { Bot, MessageCircle } from "lucide-react";

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [currentAgent, setCurrentAgent] = useState<string>("");
  const [guardrails, setGuardrails] = useState<GuardrailCheck[]>([]);
  const [context, setContext] = useState<Record<string, any>>({});
  const [conversationId, setConversationId] = useState<string | null>(null);
  // Loading state while awaiting assistant response
  const [isLoading, setIsLoading] = useState(false);
  // Mobile tab state
  const [activeTab, setActiveTab] = useState<'agent' | 'customer'>('agent');

  // Boot the conversation
  useEffect(() => {
    (async () => {
      const data = await callChatAPI("", conversationId ?? "");
      if (data) {
        setConversationId(data.conversation_id);
        setCurrentAgent(data.current_agent);
        setContext(data.context);
        const initialEvents = (data.events || []).map((e: any) => ({
          ...e,
          timestamp: e.timestamp ?? Date.now(),
        }));
        setEvents(initialEvents);
        setAgents(data.agents || []);
        setGuardrails(data.guardrails || []);
        if (Array.isArray(data.messages)) {
          setMessages(
            data.messages.map((m: any) => ({
              id: Date.now().toString() + Math.random().toString(),
              content: m.content,
              role: "assistant",
              agent: m.agent,
              timestamp: new Date(),
            }))
          );
        }
      }
    })();
  }, []);

  // Send a user message
  const handleSendMessage = async (content: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      content,
      role: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    const data = await callChatAPI(content, conversationId ?? "");

    if (data) {
      if (!conversationId) setConversationId(data.conversation_id);
      setCurrentAgent(data.current_agent);
      setContext(data.context);
      if (data.events) {
        const stamped = data.events.map((e: any) => ({
          ...e,
          timestamp: e.timestamp ?? Date.now(),
        }));
        setEvents((prev) => [...prev, ...stamped]);
      }
      if (data.agents) setAgents(data.agents);
      // Update guardrails state
      if (data.guardrails) setGuardrails(data.guardrails);

      if (data.messages) {
        const responses: Message[] = data.messages.map((m: any) => ({
          id: Date.now().toString() + Math.random().toString(),
          content: m.content,
          role: "assistant",
          agent: m.agent,
          timestamp: new Date(),
        }));
        setMessages((prev) => [...prev, ...responses]);
      }
    }

    setIsLoading(false);
  };

  return (
    <div className="relative w-full h-screen">
      <main className="flex w-full gap-2 bg-gray-100 p-2 h-full md:h-full">
        {/* 桌面端：并排显示 */}
        <div className="hidden md:flex w-full gap-2">
          <AgentPanel
            agents={agents}
            currentAgent={currentAgent}
            events={events}
            guardrails={guardrails}
            context={context}
          />
          <Chat
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </div>

        {/* 移动端：根据标签页显示对应内容 */}
        <div className="md:hidden w-full pb-16">
          {activeTab === 'agent' ? (
            <AgentPanel
              agents={agents}
              currentAgent={currentAgent}
              events={events}
              guardrails={guardrails}
              context={context}
            />
          ) : (
            <Chat
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          )}
        </div>
      </main>

      {/* 移动端底部标签页导航 */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white/80 backdrop-blur-sm border-t border-gray-200/50 shadow-lg">
        <div className="flex items-center justify-center px-4 py-2">
          <div className="flex bg-gray-100/80 rounded-full p-1">
            <button
              onClick={() => setActiveTab('agent')}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                activeTab === 'agent'
                  ? 'bg-white text-gray-800 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Bot className="h-4 w-4" />
              <span className="hidden sm:inline">Agent</span>
            </button>
            <button
              onClick={() => setActiveTab('customer')}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                activeTab === 'customer'
                  ? 'bg-white text-gray-800 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <MessageCircle className="h-4 w-4" />
              <span className="hidden sm:inline">Customer</span>
            </button>
          </div>
        </div>
      </div>
      
      {/* 开发测试面板 */}
      <DevPanel onSendMessage={handleSendMessage} />
    </div>
  );
}

export default App;
