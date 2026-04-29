import React, { useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';

interface ProcessGraphProps {
  data?: any;
  nodes?: Array<{ id: string; label: string; frequency?: number }>;
  edges?: Array<{ source: string; target: string; frequency?: number }>;
}

const NODE_WIDTH = 160;
const NODE_HEIGHT = 50;

function applyDagreLayout(
  rawNodes: any[],
  rawEdges: any[]
): { nodes: Node[]; edges: Edge[] } {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: 'LR', nodesep: 60, ranksep: 100 });

  rawNodes.forEach((n) => g.setNode(n.id, { width: NODE_WIDTH, height: NODE_HEIGHT }));
  rawEdges.forEach((e) => g.setEdge(e.source, e.target));

  dagre.layout(g);

  const nodes: Node[] = rawNodes.map((n) => {
    const pos = g.node(n.id);
    return {
      id: n.id,
      position: { x: pos.x - NODE_WIDTH / 2, y: pos.y - NODE_HEIGHT / 2 },
      data: {
        label: (
          <div className="text-center">
            <div className="font-medium text-sm">{n.label}</div>
            {n.frequency !== undefined && (
              <div className="text-xs text-gray-400">{n.frequency}×</div>
            )}
          </div>
        ),
      },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      style: {
        background: n.type === 'start' ? '#10b981' : n.type === 'end' ? '#f43f5e' : '#1e293b',
        border: '1px solid #334155',
        borderRadius: n.type === 'place' ? 50 : 8,
        color: '#f1f5f9',
        width: NODE_WIDTH,
        height: NODE_HEIGHT,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      },
    };
  });

  const edges: Edge[] = rawEdges.map((e, i) => ({
    id: `e-${i}`,
    source: e.source,
    target: e.target,
    label: e.frequency ? `${e.frequency}` : undefined,
    animated: true,
    style: { stroke: '#6366f1' },
    labelStyle: { fill: '#94a3b8', fontSize: 11 },
  }));

  return { nodes, edges };
}

const ProcessGraph: React.FC<ProcessGraphProps> = ({ data, nodes: propsNodes, edges: propsEdges }) => {
  const rawNodes = data?.places ? [...data.places, ...data.transitions] : (data?.nodes || propsNodes || []);
  const rawEdges = data?.arcs ? data.arcs : (data?.edges || propsEdges || []);

  const { nodes, edges } = useMemo(
    () => applyDagreLayout(rawNodes, rawEdges),
    [rawNodes, rawEdges]
  );

  return (
    <div style={{ width: '100%', height: 500 }} className="rounded-xl overflow-hidden border border-slate-700">
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background color="#334155" gap={20} />
        <Controls />
        <MiniMap nodeColor="#6366f1" maskColor="rgba(0,0,0,0.6)" />
      </ReactFlow>
    </div>
  );
};

export default ProcessGraph;
