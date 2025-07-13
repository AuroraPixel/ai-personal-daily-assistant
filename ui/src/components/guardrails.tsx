import { Shield, CheckCircle, XCircle } from "lucide-react";
import type { GuardrailCheck } from "../lib/types";

interface GuardrailsProps {
  guardrails: GuardrailCheck[];
  inputGuardrails: string[];
}

export function Guardrails({ guardrails, inputGuardrails }: GuardrailsProps) {
  const activeGuardrails = guardrails.filter(g => 
    inputGuardrails.includes(g.name) || inputGuardrails.includes(g.id)
  );

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Shield className="h-4 w-4 text-gray-600" />
        <h3 className="font-semibold text-sm text-gray-900">
          安全护栏检查
        </h3>
      </div>
      
      {activeGuardrails.length === 0 && (
        <div className="text-xs text-gray-500 italic">
          当前代理没有激活的护栏检查
        </div>
      )}
      
      {activeGuardrails.map((check) => (
        <div
          key={check.id}
          className={`p-3 rounded-lg border ${
            check.passed
              ? "border-green-200 bg-green-50"
              : "border-red-200 bg-red-50"
          }`}
        >
          <div className="flex items-start gap-2">
            {check.passed ? (
              <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
            ) : (
              <XCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
            )}
            <div className="flex-1">
              <h4 className="font-medium text-sm text-gray-900">
                {check.name}
              </h4>
              <p className="text-xs text-gray-600 mt-1">
                {check.reasoning}
              </p>
              <div className="text-xs text-gray-500 mt-1">
                输入: {check.input}
              </div>
            </div>
          </div>
          <div className="text-xs text-gray-400 mt-2">
            检查时间: {check.timestamp.toLocaleTimeString()}
          </div>
        </div>
      ))}
      
      {guardrails.length > activeGuardrails.length && (
        <div className="mt-4">
          <h4 className="font-medium text-xs text-gray-700 mb-2">
            所有护栏检查历史:
          </h4>
          <div className="space-y-2">
            {guardrails.map((check) => (
              <div
                key={check.id}
                className="p-2 rounded border bg-gray-50 text-xs"
              >
                <div className="flex items-center gap-2">
                  {check.passed ? (
                    <CheckCircle className="h-3 w-3 text-green-600" />
                  ) : (
                    <XCircle className="h-3 w-3 text-red-600" />
                  )}
                  <span className="font-medium">{check.name}</span>
                  <span className="text-gray-500 ml-auto">
                    {check.timestamp.toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 