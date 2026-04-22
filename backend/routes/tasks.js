const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');

// Task Schema
const taskSchema = new mongoose.Schema({
  title:       { type: String, required: true, trim: true },
  description: { type: String, trim: true, default: '' },
  priority:    { type: String, enum: ['low', 'medium', 'high'], default: 'medium' },
  status:      { type: String, enum: ['pending', 'in-progress', 'completed'], default: 'pending' },
  dueDate:     { type: Date },
  createdAt:   { type: Date, default: Date.now }
});

const Task = mongoose.model('Task', taskSchema);

// GET all tasks
router.get('/', async (req, res) => {
  try {
    const { status, priority } = req.query;
    const filter = {};
    if (status)   filter.status   = status;
    if (priority) filter.priority = priority;
    const tasks = await Task.find(filter).sort({ createdAt: -1 });
    res.json(tasks);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET single task by ID
router.get('/:id', async (req, res) => {
  try {
    const task = await Task.findById(req.params.id);
    if (!task) return res.status(404).json({ error: 'Task not found' });
    res.json(task);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST create a task
router.post('/', async (req, res) => {
  try {
    const task = new Task(req.body);
    await task.save();
    res.status(201).json(task);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// PATCH update a task (status, priority, etc.)
router.patch('/:id', async (req, res) => {
  try {
    const task = await Task.findByIdAndUpdate(
      req.params.id,
      { $set: req.body },
      { new: true, runValidators: true }
    );
    if (!task) return res.status(404).json({ error: 'Task not found' });
    res.json(task);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// DELETE a task
router.delete('/:id', async (req, res) => {
  try {
    const task = await Task.findByIdAndDelete(req.params.id);
    if (!task) return res.status(404).json({ error: 'Task not found' });
    res.json({ message: 'Task deleted successfully' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
