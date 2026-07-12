'use client';

import { useState } from 'react';
import * as SelectPrimitive from '@radix-ui/react-select';
import { ChevronDown } from 'lucide-react';
import { Select, SelectContent, SelectItem } from '@/components/ui/select';
import { cn } from '@/lib/utils';
import { ResearchHistoryItem } from '@/lib/use-research-history';

interface ResearchPickerProps {
  history: ResearchHistoryItem[];
  loading?: boolean;
  onSelect: (jobId: string) => void;
  placeholder?: string;
  className?: string;
}

/** Dropdown for picking a completed research job from the user's history. */
export function ResearchPicker({
  history, loading, onSelect,
  placeholder = 'Select a completed research run…',
  className,
}: ResearchPickerProps) {
  const [open, setOpen] = useState(false);

  if (loading) {
    return <div className={cn('w-full h-10 rounded-lg bg-white/5 border border-white/10 animate-pulse', className)} />;
  }

  const isEmpty = history.length === 0;

  return (
    <Select open={open} onOpenChange={setOpen} onValueChange={onSelect}>
      {/* Built raw (not via the shared SelectTrigger) so there's exactly one chevron, not two competing for the same spot. */}
      <SelectPrimitive.Trigger
        className={cn(
          'flex w-full items-center justify-between gap-2 rounded-lg bg-white/5 border border-white/10 px-4 py-2.5',
          'text-white text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/50 overflow-hidden',
          className
        )}
      >
        <SelectPrimitive.Value
          placeholder={isEmpty ? 'No research history to choose' : placeholder}
          className="flex-1 min-w-0 truncate text-left block"
        />
        <SelectPrimitive.Icon asChild>
          <ChevronDown
            className={cn(
              'h-4 w-4 opacity-50 shrink-0 mr-1 transition-transform duration-200',
              open && 'rotate-180'
            )}
          />
        </SelectPrimitive.Icon>
      </SelectPrimitive.Trigger>
      <SelectContent
        className="bg-gray-900 border-white/10 text-white w-[var(--radix-select-trigger-width)] max-w-[calc(100vw-2rem)]"
        sideOffset={6}
        align="start"
        avoidCollisions
      >
        {isEmpty ? (
          <div className="px-8 py-3 text-sm text-gray-500">No research history to choose</div>
        ) : (
          history.map((h) => (
            <SelectItem key={h.job_id} value={h.job_id} className="text-sm focus:bg-white/10 focus:text-white">
              <span className="block truncate max-w-full">
                {(h.idea ?? 'Untitled').slice(0, 40)}
                {h.industry ? ` · ${h.industry}` : ''}
                {h.innovation_score != null ? ` · ${h.innovation_score}` : ''}
              </span>
            </SelectItem>
          ))
        )}
      </SelectContent>
    </Select>
  );
}
