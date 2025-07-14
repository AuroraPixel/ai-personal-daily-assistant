import { Bot } from "lucide-react";
import type { Agent, AgentEvent, GuardrailCheck } from "../lib/types";
import { AgentsList } from "./agents-list";
import { Guardrails } from "./guardrails";
import { ConversationContext } from "./conversation-context";
import { RunnerOutput } from "./runner-output";
import { PanelSection } from "./panel-section";

interface AgentPanelProps {
  agents: Agent[];
  currentAgent: string;
  events: AgentEvent[];
  guardrails: GuardrailCheck[];
  context: {
    passenger_name?: string;
    confirmation_number?: string;
    seat_number?: string;
    flight_number?: string;
    account_number?: string;
  };
}

export function AgentPanel({
  agents,
  currentAgent,
  events,
  guardrails,
  context,
}: AgentPanelProps) {
  const activeAgent = agents.find((a) => a.name === currentAgent);
  const runnerEvents = events.filter((e) => e.type !== "message");

  return (
    <div className="w-full h-full flex flex-col border-r border-gray-200 bg-white rounded-xl shadow-sm">
      <div className="bg-blue-600 text-white h-12 px-4 flex items-center gap-3 shadow-sm rounded-t-xl flex-shrink-0">
        <Bot className="h-5 w-5" />
        <h1 className="font-semibold text-sm sm:text-base lg:text-lg">Agent View</h1>
        <span className="ml-auto text-xs font-light tracking-wide opacity-80">
          &nbsp;Personal Assistant
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-6 bg-gray-50/50 space-y-6">
        <PanelSection title="代理状态" defaultOpen={true}>
          <AgentsList agents={agents} currentAgent={currentAgent} />
        </PanelSection>

        {/* 安全护栏功能已暂时隐藏 */}
        {/*
        <PanelSection title="安全护栏" defaultOpen={true}>
          <Guardrails
            guardrails={guardrails}
            inputGuardrails={activeAgent?.input_guardrails ?? []}
          />
        </PanelSection>
        */}

        <PanelSection title="对话上下文" defaultOpen={true}>
          <ConversationContext context={context} />
        </PanelSection>

        <PanelSection title="运行输出" defaultOpen={true}>
          <RunnerOutput runnerEvents={runnerEvents} />
        </PanelSection>
      </div>
    </div>
  );
} 